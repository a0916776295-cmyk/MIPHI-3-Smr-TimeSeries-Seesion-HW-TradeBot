import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings

# Отключаем предупреждения yfinance
warnings.filterwarnings('ignore', category=FutureWarning)

def get_finance_data(ticker: str) -> pd.DataFrame | None:
    """
    Загружает финансовые данные для указанного тикера
    
    Args:
        ticker: Тикер актива (например, 'AAPL')
    
    Returns:
        DataFrame с данными или None в случае ошибки
    """
    try:
        print(f"Loading data for {ticker}...")
        
        end = datetime.today()
        start = end - timedelta(days=730)  # 2 года данных

        # Загружаем данные с исправленными параметрами
        df = yf.download(
            ticker, 
            start=start, 
            end=end, 
            progress=False,
            auto_adjust=True,  # Явно указываем auto_adjust
            prepost=True,      # Включаем пре- и пост-маркетинг
            threads=True       # Многопоточность для быстрой загрузки
        )
        
        if df is None or df.empty:
            print(f"No data received for {ticker}")
            return None
        
        # Если колонки имеют мультииндекс (при загрузке одного тикера их не должно быть)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        
        # Убираем NaN значения
        df = df.dropna()
        
        # Убеждаемся, что индекс - это DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Проверяем наличие обязательных колонок
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing columns for {ticker}: {missing_columns}")
            return None
        
        print(f"Successfully loaded {len(df)} records for {ticker}")
        print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"Latest close price: ${df['Close'].iloc[-1]:.2f}")
        
        return df
        
    except Exception as e:
        print(f"Error loading data for {ticker}: {str(e)}")
        # Логируем дополнительную информацию для отладки
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return None
