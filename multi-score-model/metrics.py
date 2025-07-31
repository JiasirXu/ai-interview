from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
import numpy as np

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    mse = mean_squared_error(labels, predictions)
    mae = mean_absolute_error(labels, predictions)
    
    # 计算每个标签的Pearson相关系数
    pearson_scores = []
    for i in range(labels.shape[1]):
        # 确保有足够的样本来计算相关性
        if len(np.unique(labels[:, i])) > 1 and len(np.unique(predictions[:, i])) > 1:
            corr, _ = pearsonr(labels[:, i], predictions[:, i])
            pearson_scores.append(corr)
        else:
            pearson_scores.append(0.0) # 如果数据不足，相关性为0

    avg_pearson = np.mean(pearson_scores) if pearson_scores else 0.0

    return {
        "mse": mse,
        "mae": mae,
        "pearson": avg_pearson,
    }


