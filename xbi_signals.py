import numpy as np
import pandas as pd

class XBISignalGenerator:
    def __init__(self, df):
        """
        Initialize signal generator with price data
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data
        """
        self.df = df.copy()
        self.signals = pd.DataFrame(index=df.index)
    
    def calculate_rsi_signals(self, period=14, upper=70, lower=30):
        """
        Generate RSI-based signals
        
        Args:
            period (int): RSI calculation period
            upper (float): Overbought threshold
            lower (float): Oversold threshold
        
        Returns:
            pd.Series: RSI signals
        """
        rsi = ta.momentum.RSIIndicator(
            close=self.df['close'], 
            window=period
        ).rsi()
        
        self.signals['rsi'] = rsi
        self.signals['rsi_buy_signal'] = (rsi < lower).astype(int)
        self.signals['rsi_sell_signal'] = (rsi > upper).astype(int)
        
        return self.signals['rsi']
    
    def calculate_bollinger_signals(self, period=20, dev=2):
        """
        Generate Bollinger Band signals
        
        Args:
            period (int): Bollinger Band period
            dev (float): Standard deviation multiplier
        
        Returns:
            pd.DataFrame: Bollinger Band signals
        """
        bollinger = ta.volatility.BollingerBands(
            close=self.df['close'], 
            window=period, 
            window_dev=dev
        )
        
        self.signals['bollinger_lower'] = bollinger.bollinger_lband()
        self.signals['bollinger_upper'] = bollinger.bollinger_hband()
        
        # Buy when price touches lower band
        self.signals['bollinger_buy_signal'] = (
            self.df['close'] <= self.signals['bollinger_lower']
        ).astype(int)
        
        # Sell when price touches upper band
        self.signals['bollinger_sell_signal'] = (
            self.df['close'] >= self.signals['bollinger_upper']
        ).astype(int)
        
        return self.signals[['bollinger_lower', 'bollinger_upper']]
    
    def calculate_macd_signals(self, fast=12, slow=26, signal=9):
        """
        Generate MACD signals
        
        Args:
            fast (int): Fast period
            slow (int): Slow period
            signal (int): Signal line period
        
        Returns:
            pd.Series: MACD signals
        """
        macd = ta.trend.MACD(
            close=self.df['close'], 
            window_slow=slow, 
            window_fast=fast, 
            window_sign=signal
        )
        
        self.signals['macd'] = macd.macd()
        self.signals['macd_signal'] = macd.macd_signal()
        
        # Buy when MACD crosses above signal line
        self.signals['macd_buy_signal'] = (
            (self.signals['macd'] > self.signals['macd_signal']) & 
            (self.signals['macd'].shift(1) <= self.signals['macd_signal'].shift(1))
        ).astype(int)
        
        # Sell when MACD crosses below signal line
        self.signals['macd_sell_signal'] = (
            (self.signals['macd'] < self.signals['macd_signal']) & 
            (self.signals['macd'].shift(1) >= self.signals['macd_signal'].shift(1))
        ).astype(int)
        
        return self.signals['macd']
    
    def calculate_composite_signal(self):
        """
        Generate composite buy/sell signals
        
        Returns:
            pd.DataFrame: Composite signals
        """
        # Combine signals with weighted approach
        self.signals['composite_buy_signal'] = (
            self.signals['rsi_buy_signal'] * 0.4 +
            self.signals['bollinger_buy_signal'] * 0.3 +
            self.signals['macd_buy_signal'] * 0.3
        )
        
        self.signals['composite_sell_signal'] = (
            self.signals['rsi_sell_signal'] * 0.4 +
            self.signals['bollinger_sell_signal'] * 0.3 +
            self.signals['macd_sell_signal'] * 0.3
        )
        
        # Normalize signals
        self.signals['composite_buy_signal'] = (
            self.signals['composite_buy_signal'] > 0.5
        ).astype(int)
        
        self.signals['composite_sell_signal'] = (
            self.signals['composite_sell_signal'] > 0.5
        ).astype(int)
        
        return self.signals[['composite_buy_signal', 'composite_sell_signal']]
    
    def get_final_signals(self):
        """
        Retrieve final signals
        
        Returns:
            pd.DataFrame: Comprehensive signals
        """
        # Ensure all signal calculations are complete
        self.calculate_rsi_signals()
        self.calculate_bollinger_signals()
        self.calculate_macd_signals()
        self.calculate_composite_signal()
        
        return self.signals

def load_and_prepare_data(filepath):
    """
    Load and preprocess financial data
    
    Args:
        filepath (str): Path to CSV file
    
    Returns:
        pd.DataFrame: Processed DataFrame
    """
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    return df

def main():
    # Example usage
    df = load_and_prepare_data('xbi_data.csv')
    signal_generator = XBISignalGenerator(df)
    
    # Get comprehensive signals
    signals = signal_generator.get_final_signals()
    print(signals.head())

if __name__ == "__main__":
    main()