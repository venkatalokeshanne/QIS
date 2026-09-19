"""Tests for app.services.calibration_store."""

from app.services import calibration_store
from app.services.calibration_service import TickerProfile


def _profile(symbol="IONQ"):
    return TickerProfile(
        symbol=symbol,
        interval="15min",
        calibrated_through="2026-04-30",
        market_proxies=["SPY", "QQQ"],
        default_strategy="sma_cross",
        strategy_by_regime={"ticker=trending/high_vol|market=trending/low_vol": "adr_exhaustion_fade"},
        regime_trade_counts={"ticker=trending/high_vol|market=trending/low_vol": 12},
        stop_loss_atr_multiple=1.5,
        take_profit_atr_multiple=3.0,
        entry_time_start="09:30",
        entry_time_end="11:30",
        regime_params={},
    )


def test_load_profile_returns_none_for_uncalibrated_symbol(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration_store.settings, "data_dir", tmp_path)
    assert calibration_store.load_profile("NOPE") is None


def test_save_then_load_round_trips(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration_store.settings, "data_dir", tmp_path)
    profile = _profile()

    calibration_store.save_profile(profile)
    loaded = calibration_store.load_profile("ionq")  # lowercase -- symbol lookup is case-insensitive

    assert loaded == profile


def test_save_writes_under_data_dir_calibration(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration_store.settings, "data_dir", tmp_path)
    calibration_store.save_profile(_profile("IONQ"))

    assert (tmp_path / "calibration" / "IONQ.json").exists()


def test_load_all_profiles_returns_every_saved_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration_store.settings, "data_dir", tmp_path)
    calibration_store.save_profile(_profile("IONQ"))
    calibration_store.save_profile(_profile("NVDA"))

    profiles = calibration_store.load_all_profiles()

    assert set(profiles.keys()) == {"IONQ", "NVDA"}
    assert profiles["NVDA"].symbol == "NVDA"


def test_load_all_profiles_empty_when_nothing_calibrated_yet(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration_store.settings, "data_dir", tmp_path)
    assert calibration_store.load_all_profiles() == {}


def test_save_overwrites_an_existing_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration_store.settings, "data_dir", tmp_path)
    calibration_store.save_profile(_profile("IONQ"))

    updated = TickerProfile(**{**_profile("IONQ").__dict__, "default_strategy": "vwap_reversion"})
    calibration_store.save_profile(updated)

    assert calibration_store.load_profile("IONQ").default_strategy == "vwap_reversion"
