"""Zamanlama — "dipten al, tepeden sat" iddiasını sayısal olarak sınayan geri-test motoru.

Amaç bir strateji satmak değil; literatürdeki iddiaları (hareketli ortalama
zamanlaması, gecikme maliyeti, veri-madenciliği/parametre kalıcılığı,
"mükemmel zamanlama" üst sınırı) aynı veri üzerinde tekrar üretilebilir
biçimde ölçmektir. Bkz. docs/dip_al_tepe_sat_literatur_raporu.md
"""

from .motor import (  # noqa: F401
    Sonuc,
    al_ve_tut,
    dip_tepe_kahini,
    gecikme_analizi,
    geri_test,
    ileriye_donuk,
    kesisim_kurali,
    mukemmel_ongoru,
    sma_kurali,
    veri_yukle,
)
