#!/usr/bin/env python3
"""
Hyperliquid Funding Rate Analyzer
Identifies high-funding assets and potential arbitrage opportunities.

Portfolio Value:
- Real API integration (Hyperliquid public endpoints)
- Time-series analysis with pandas
- Statistical pattern detection
- Trading signal generation
- Clean CLI with argument parsing

Author: Yumo Xu
Created: 2026-03-13
"""

import requests
import pandas as pd
import argparse
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional


class HyperliquidFundingAnalyzer:
    """Analyzes Hyperliquid perpetual funding rates for trading opportunities."""
    
    BASE_URL = "https://api.hyperliquid.xyz/info"
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _log(self, message: str):
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def get_meta_and_asset_ctxs(self) -> tuple:
        """Fetch market metadata and asset contexts (funding, OI, prices)."""
        self._log("Fetching market metadata and asset contexts...")
        payload = {"type": "metaAndAssetCtxs"}
        response = self.session.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data[0], data[1]  # meta, assetCtxs
    
    def get_all_mids(self) -> Dict[str, float]:
        """Fetch current mid prices for all assets."""
        self._log("Fetching current prices...")
        payload = {"type": "allMids"}
        response = self.session.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_funding_history(self, coin: str, start_time: int, end_time: Optional[int] = None) -> List[Dict]:
        """
        Fetch historical funding rates for a coin.
        
        Args:
            coin: Asset symbol (e.g., 'BTC', 'ETH')
            start_time: Unix timestamp in milliseconds
            end_time: Optional end timestamp (defaults to now)
        """
        self._log(f"Fetching funding history for {coin}...")
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_time
        }
        if end_time:
            payload["endTime"] = end_time
        
        response = self.session.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    
    def analyze_current_funding(self, top_n: int = 20) -> pd.DataFrame:
        """
        Analyze current funding rates across all perpetuals.
        
        Returns:
            DataFrame with coins sorted by absolute funding rate
        """
        print("\n🔍 Analyzing current funding rates...\n")
        
        # Get market metadata and asset contexts
        meta, asset_ctxs = self.get_meta_and_asset_ctxs()
        universe = meta.get('universe', [])
        
        # Build analysis DataFrame
        data = []
        for i, asset in enumerate(universe):
            coin = asset['name']
            
            # Skip delisted assets
            if asset.get('isDelisted', False):
                continue
            
            # Get asset context (funding, price, OI, etc.)
            ctx = asset_ctxs[i] if i < len(asset_ctxs) else {}
            
            funding = float(ctx.get('funding', 0))
            price = float(ctx.get('markPx', 0))
            open_interest = float(ctx.get('openInterest', 0))
            volume_24h = float(ctx.get('dayNtlVlm', 0))
            
            # Calculate annualized funding rate (8-hour periods, 3x per day, 365 days)
            annual_rate = funding * 3 * 365 * 100  # Convert to percentage
            
            data.append({
                'coin': coin,
                'funding_8h': funding,
                'funding_annual_pct': annual_rate,
                'abs_funding': abs(funding),
                'price': price,
                'open_interest': open_interest,
                'volume_24h': volume_24h,
                'direction': 'LONG_PAYS' if funding > 0 else 'SHORT_PAYS'
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('abs_funding', ascending=False)
        
        # Display top results
        print(f"📊 Top {top_n} Assets by Funding Rate:\n")
        print("-" * 100)
        print(f"{'Coin':<10} {'8H Rate':<12} {'Annual %':<12} {'Price':<12} {'OI ($M)':<12} {'Direction':<15}")
        print("-" * 100)
        
        for _, row in df.head(top_n).iterrows():
            oi_millions = (row['open_interest'] * row['price']) / 1_000_000
            print(f"{row['coin']:<10} {row['funding_8h']:>11.8f} {row['funding_annual_pct']:>11.2f} "
                  f"${row['price']:>10.2f} ${oi_millions:>10.1f} {row['direction']:<15}")
        
        print("-" * 100)
        
        # Summary statistics
        positive_funding = df[df['funding_8h'] > 0]
        negative_funding = df[df['funding_8h'] < 0]
        
        print(f"\n📈 Summary:")
        print(f"  • Total assets: {len(df)}")
        print(f"  • Positive funding (longs pay shorts): {len(positive_funding)}")
        print(f"  • Negative funding (shorts pay longs): {len(negative_funding)}")
        print(f"  • Mean 8H funding rate: {df['funding_8h'].mean():.6f}")
        print(f"  • Median 8H funding rate: {df['funding_8h'].median():.6f}")
        
        return df
    
    def find_arbitrage_opportunities(self, df: pd.DataFrame, threshold: float = 0.001) -> None:
        """
        Identify potential arbitrage opportunities based on extreme funding rates.
        
        Args:
            df: DataFrame from analyze_current_funding()
            threshold: Minimum absolute 8H funding rate to flag (default 0.1%)
        """
        print(f"\n💡 Arbitrage Opportunities (|funding| > {threshold*100:.2f}%):\n")
        
        extreme = df[df['abs_funding'] > threshold].copy()
        
        if extreme.empty:
            print(f"  No opportunities found above {threshold*100:.2f}% threshold.")
            return
        
        print("=" * 100)
        for _, row in extreme.iterrows():
            if row['funding_8h'] > 0:
                strategy = "🔴 SHORT + earn funding from longs"
                risk = "Risk: Avoid if strong uptrend (funding can stay high)"
            else:
                strategy = "🟢 LONG + earn funding from shorts"
                risk = "Risk: Avoid if strong downtrend (funding can stay negative)"
            
            oi_millions = (row['open_interest'] * row['price']) / 1_000_000
            
            print(f"\n{row['coin']}:")
            print(f"  • 8H Rate: {row['funding_8h']:.8f} ({row['funding_annual_pct']:+.2f}% annualized)")
            print(f"  • Price: ${row['price']:.2f}")
            print(f"  • Open Interest: ${oi_millions:.1f}M")
            print(f"  • {strategy}")
            print(f"  • {risk}")
        
        print("\n" + "=" * 100)
    
    def export_csv(self, df: pd.DataFrame, filename: str = "funding_analysis.csv") -> None:
        """Export analysis results to CSV."""
        df.to_csv(filename, index=False)
        print(f"\n💾 Results exported to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Hyperliquid perpetual funding rates for arbitrage opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current funding rates
  python3 funding_analyzer.py
  
  # Show top 30 assets with verbose logging
  python3 funding_analyzer.py --top 30 --verbose
  
  # Export results to CSV
  python3 funding_analyzer.py --export funding_2026_03_13.csv
  
  # Find high-conviction opportunities (>0.2% 8H funding)
  python3 funding_analyzer.py --threshold 0.002
        """
    )
    
    parser.add_argument('--top', type=int, default=20,
                        help='Number of top assets to display (default: 20)')
    parser.add_argument('--threshold', type=float, default=0.001,
                        help='Minimum abs funding rate for arbitrage flag (default: 0.001 = 0.1%%)')
    parser.add_argument('--export', type=str, metavar='FILE',
                        help='Export results to CSV file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        analyzer = HyperliquidFundingAnalyzer(verbose=args.verbose)
        
        # Run analysis
        df = analyzer.analyze_current_funding(top_n=args.top)
        
        # Find arbitrage opportunities
        analyzer.find_arbitrage_opportunities(df, threshold=args.threshold)
        
        # Export if requested
        if args.export:
            analyzer.export_csv(df, filename=args.export)
        
        print("\n✅ Analysis complete.\n")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
