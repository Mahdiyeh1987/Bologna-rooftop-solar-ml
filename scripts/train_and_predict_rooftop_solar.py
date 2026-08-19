# Rooftop solar modeling and citywide prediction
# Paths
TRAIN_PATH = r"C:\GIS\work\train_dataset.csv"
INFER_PATH = r"C:\GIS\work\inference_features.csv"
PRED_OUT   = r"C:\GIS\work\predictions_city.csv"
IMP_OUT    = r"C:\GIS\work\feature_importance.csv"
MODEL_TXT  = r"C:\GIS\work\model_lgbm.txt"   # optional
MODEL_PKL  = r"C:\GIS\work\model_lgbm.pkl"   # optional

# -------------------- Imports --------------------
import json, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import GroupKFold

# Prefer StratifiedGroupKFold if available
try:
    from sklearn.model_selection import StratifiedGroupKFold
    HAS_SGF = True
except Exception:
    HAS_SGF = False

# Models
USE_LGBM = True
try:
    import lightgbm as lgb
except Exception:
    USE_LGBM = False

USE_XGB = False
if not USE_LGBM:
    try:
        import xgboost as xgb
        USE_XGB = True
    except Exception:
        pass

if (not USE_LGBM) and (not USE_XGB):
    raise ImportError("Neither lightgbm nor xgboost is available. Please install one of them.")

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# -------------------- Helpers --------------------
EXCLUDE_COLS = {
    "roof_id", "label_mean", "admin_flag", "stratum",
    "z_admin", "z_admin_code", "z_morph_k4"
}

def load_train_infer(train_path, infer_path):
    return pd.read_csv(train_path), pd.read_csv(infer_path)

def make_groups_and_bins(df, target_col="label_mean"):
    za = df.get("z_admin")
    zm = df.get("z_morph_k4")
    if za is None and zm is None:
        groups = pd.Series("ungrouped", index=df.index)
    elif zm is None:
        groups = za.astype(str)
    elif za is None:
        groups = zm.astype(str)
    else:
        groups = (za.astype(str) + "_" + zm.astype(str))

    y = df[target_col].astype(float)
    n_bins = 10
    try:
        y_bins = pd.qcut(y, q=n_bins, labels=False, duplicates="drop")
    except Exception:
        ranks = y.rank(method="average", pct=True)
        y_bins = np.floor(ranks * n_bins).clip(0, n_bins-1).astype(int)
    return groups, y_bins

def select_features(df: pd.DataFrame, target_col="label_mean"):
    cols = []
    for c in df.columns:
        if c in EXCLUDE_COLS or c == target_col:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            cols.append(c)
    return cols

def drop_low_variance_and_dupes(df, cols, tol=1e-8):
    """Remove near-constant features and duplicate names (safety)."""
    clean, seen = [], set()
    for c in cols:
        if c in seen:
            continue
        seen.add(c)
        s = df[c].astype(float)
        if s.var() <= tol:
            continue
        clean.append(c)
    return clean

def align_inference_columns(df_inf, feat_cols):
    for c in feat_cols:
        if c not in df_inf.columns:
            df_inf[c] = 0.0
    return df_inf[feat_cols].copy()

def save_feature_importance(imp_series: pd.Series, out_path: str):
    imp_df = imp_series.reset_index()
    imp_df.columns = ["feature", "importance"]
    imp_df.sort_values("importance", ascending=False, inplace=True)
    imp_df.to_csv(out_path, index=False)

# -------------------- Load --------------------
df_train, df_inf = load_train_infer(TRAIN_PATH, INFER_PATH)

for col in ["roof_id", "label_mean"]:
    if col not in df_train.columns:
        raise ValueError(f"Required column '{col}' missing in train_dataset.csv")
if "roof_id" not in df_inf.columns:
    raise ValueError("Required column 'roof_id' missing in inference_features.csv")

# -------------------- Prepare --------------------
groups, y_bins = make_groups_and_bins(df_train, target_col="label_mean")
feat_cols = select_features(df_train, target_col="label_mean")
feat_cols = drop_low_variance_and_dupes(df_train, feat_cols)
print(f"Using {len(feat_cols)} features after cleaning.")

if len(feat_cols) == 0:
    raise ValueError("No usable numeric feature columns found after cleaning.")

X_all = df_train[feat_cols].astype(float).values
y_all = df_train["label_mean"].astype(float).values

n_splits = 5
if HAS_SGF:
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    split_iter = splitter.split(X_all, y_bins, groups)
else:
    splitter = GroupKFold(n_splits=n_splits)
    split_iter = splitter.split(X_all, groups=groups)

train_idx, test_idx = next(split_iter)
X_tr, X_te = X_all[train_idx], X_all[test_idx]
y_tr, y_te = y_all[train_idx], y_all[test_idx]

# -------------------- Train --------------------
if USE_LGBM:
    model = lgb.LGBMRegressor(
        n_estimators=2000,
        learning_rate=0.02,
        num_leaves=127,
        max_depth=-1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=0.5,
        min_child_samples=10,
        max_bin=511,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    model.fit(
        X_tr, y_tr,
        eval_set=[(X_te, y_te)],
        eval_metric="l2",
        callbacks=[lgb.early_stopping(stopping_rounds=150, verbose=False)]
    )
elif USE_XGB:
    model = xgb.XGBRegressor(
        n_estimators=2000,
        learning_rate=0.03,
        max_depth=9,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=0.5,
        min_child_weight=1,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
        max_bin=511
    )
    model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], eval_metric="rmse", verbose=False)
else:
    raise RuntimeError("No model backend available.")

# -------------------- Evaluate --------------------
y_hat_test = model.predict(X_te)
r2  = r2_score(y_te, y_hat_test)
mae = mean_absolute_error(y_te, y_hat_test)
print(json.dumps({"TEST_R2": round(float(r2), 4), "TEST_MAE_kWhm2yr": round(float(mae), 2)}, indent=2))

# -------------------- Importance --------------------
try:
    imp = pd.Series(model.feature_importances_, index=feat_cols)
except Exception:
    imp = pd.Series(np.nan, index=feat_cols)
save_feature_importance(imp, IMP_OUT)

# -------------------- Inference --------------------
X_inf = align_inference_columns(df_inf, feat_cols).astype(float).values
y_hat_inf = model.predict(X_inf)
pd.DataFrame({"roof_id": df_inf["roof_id"], "y_hat_kWhm2yr": y_hat_inf}).to_csv(PRED_OUT, index=False)

# -------------------- Save model (optional) --------------------
try:
    if USE_LGBM:
        model.booster_.save_model(MODEL_TXT)
    else:
        model.get_booster().dump_model(MODEL_TXT)
except Exception:
    pass

try:
    import joblib
    joblib.dump(model, MODEL_PKL)
except Exception:
    pass
