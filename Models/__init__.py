# Models package initialization
# Этот файл делает папку Models пакетом Python

# Импорт всех моделей для упрощения доступа
from . import Model_ARIMA
from . import Model_SARIMA
from . import Model_Prophet
from . import Model_LSTM
from . import Model_LSTM_optimized
from . import Model_GRU
from . import Model_GRU_optimized
from . import Model_TFT
from . import Model_Autoformer
from . import Model_FEDformer
from . import Model_Ridge
from . import Model_RandomForest
from . import Model_XGBoost
from . import Model_CatBoost
from . import Model_Transformer
from . import Model_Informer
from . import Model_Ensemble

# Импорт основной функции сравнения
from .model_comparison import compare_all_models

__version__ = "1.0.0"
__all__ = [
    "Model_ARIMA", "Model_SARIMA", "Model_Prophet", "Model_LSTM", "Model_LSTM_optimized",
    "Model_GRU", "Model_GRU_optimized", "Model_TFT", "Model_Autoformer", "Model_FEDformer", 
    "Model_Ridge", "Model_RandomForest", "Model_XGBoost", "Model_CatBoost", 
    "Model_Transformer", "Model_Informer", "Model_Ensemble",
    "compare_all_models"
]