import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import { useResearchStore } from '../store/useResearchStore'

export default function Settings() {
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const setExecutionSettings = useResearchStore((s) => s.setExecutionSettings)

  const toNullableNumber = (v) => (v === '' ? null : Number(v))

  return (
    <div>
      <PageHeader
        title="Settings"
        subtitle="Execution and risk-management defaults used by every backtest run, whether triggered from the strategy sidebar or Run Backtests."
      />

      <Card style={{ maxWidth: 480 }}>
        <div className="section-label">Execution</div>

        <div className="field-group">
          <label className="field-label">Default capital</label>
          <input
            type="number"
            className="field-input"
            value={executionSettings.capital}
            onChange={(e) => setExecutionSettings({ capital: Number(e.target.value) })}
          />
        </div>

        <div className="field-group">
          <label className="field-label">Default quantity per trade</label>
          <input
            type="number"
            className="field-input"
            value={executionSettings.quantity}
            onChange={(e) => setExecutionSettings({ quantity: Number(e.target.value) })}
          />
        </div>

        <div className="field-group">
          <label className="field-label">Default commission per trade</label>
          <input
            type="number"
            className="field-input"
            value={executionSettings.commission_per_trade}
            onChange={(e) => setExecutionSettings({ commission_per_trade: Number(e.target.value) })}
          />
        </div>

        <div className="field-group">
          <label className="field-label">Default slippage (%)</label>
          <input
            type="number"
            step="0.01"
            className="field-input"
            value={executionSettings.slippage_pct * 100}
            onChange={(e) => setExecutionSettings({ slippage_pct: Number(e.target.value) / 100 })}
          />
        </div>

        <div className="field-group">
          <label className="field-label">Trade direction</label>
          <select
            className="field-input"
            value={executionSettings.direction_filter}
            onChange={(e) => setExecutionSettings({ direction_filter: e.target.value })}
          >
            <option value="both">Long &amp; Short</option>
            <option value="long_only">Long only</option>
            <option value="short_only">Short only</option>
          </select>
        </div>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={executionSettings.force_close_at_session_end}
            onChange={(e) => setExecutionSettings({ force_close_at_session_end: e.target.checked })}
          />
          <span>Force close at session end</span>
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={executionSettings.include_extended_hours}
            onChange={(e) => setExecutionSettings({ include_extended_hours: e.target.checked })}
          />
          <span>Include extended hours (pre-/after-market)</span>
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={executionSettings.include_overnight}
            onChange={(e) => setExecutionSettings({ include_overnight: e.target.checked })}
          />
          <span>Include overnight session</span>
        </label>
      </Card>

      <Card style={{ maxWidth: 480, marginTop: 16 }}>
        <div className="section-label">Risk Management</div>

        <div className="field-group">
          <label className="field-label">ATR Period</label>
          <input
            type="number"
            className="field-input"
            value={executionSettings.atr_period}
            onChange={(e) => setExecutionSettings({ atr_period: Number(e.target.value) })}
          />
          <span className="field-hint">Used by any risk setting below that's enabled.</span>
        </div>

        <div className="field-group">
          <label className="field-label">Stop Loss (× ATR)</label>
          <input
            type="number"
            step="0.1"
            className="field-input"
            placeholder="Disabled"
            value={executionSettings.stop_loss_atr_multiple ?? ''}
            onChange={(e) =>
              setExecutionSettings({ stop_loss_atr_multiple: toNullableNumber(e.target.value) })
            }
          />
          <span className="field-hint">Ignored if Stop Loss (%) is also set.</span>
        </div>

        <div className="field-group">
          <label className="field-label">Stop Loss (%)</label>
          <input
            type="number"
            step="0.1"
            className="field-input"
            placeholder="Disabled"
            value={
              executionSettings.stop_loss_pct !== null ? executionSettings.stop_loss_pct * 100 : ''
            }
            onChange={(e) => {
              const n = toNullableNumber(e.target.value)
              setExecutionSettings({ stop_loss_pct: n === null ? null : n / 100 })
            }}
          />
          <span className="field-hint">Flat % of entry price. Takes precedence over Stop Loss (× ATR).</span>
        </div>

        <div className="field-group">
          <label className="field-label">Take Profit (× ATR)</label>
          <input
            type="number"
            step="0.1"
            className="field-input"
            placeholder="Disabled"
            value={executionSettings.take_profit_atr_multiple ?? ''}
            onChange={(e) =>
              setExecutionSettings({ take_profit_atr_multiple: toNullableNumber(e.target.value) })
            }
          />
        </div>

        <div className="field-group">
          <label className="field-label">Trailing Stop (× ATR)</label>
          <input
            type="number"
            step="0.1"
            className="field-input"
            placeholder="Disabled"
            value={executionSettings.trailing_stop_atr_multiple ?? ''}
            onChange={(e) =>
              setExecutionSettings({ trailing_stop_atr_multiple: toNullableNumber(e.target.value) })
            }
          />
          <span className="field-hint">Takes precedence over both Stop Loss settings if set.</span>
        </div>

        <div className="field-group">
          <label className="field-label">Risk per trade (%)</label>
          <input
            type="number"
            step="0.1"
            className="field-input"
            placeholder="Disabled"
            value={
              executionSettings.risk_per_trade_pct !== null
                ? executionSettings.risk_per_trade_pct * 100
                : ''
            }
            onChange={(e) => {
              const n = toNullableNumber(e.target.value)
              setExecutionSettings({ risk_per_trade_pct: n === null ? null : n / 100 })
            }}
          />
          <span className="field-hint">Requires a Stop Loss or Trailing Stop to be set.</span>
        </div>

        <div className="field-group">
          <label className="field-label">Max position value (% of capital)</label>
          <input
            type="number"
            step="1"
            className="field-input"
            placeholder="Disabled"
            value={
              executionSettings.max_position_value_pct !== null &&
              executionSettings.max_position_value_pct !== undefined
                ? executionSettings.max_position_value_pct * 100
                : ''
            }
            onChange={(e) => {
              const n = toNullableNumber(e.target.value)
              setExecutionSettings({ max_position_value_pct: n === null ? null : n / 100 })
            }}
          />
          <span className="field-hint">
            Caps shares so position value never exceeds this % of capital. 100 = full capital, no
            leverage. Blank = uncapped.
          </span>
        </div>
      </Card>
    </div>
  )
}
