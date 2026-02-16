#######################################################
# imports
import ngehtsim.obs.obs_generator as og
import ehtim as eh
import astropy
import os

#######################################################
# generate an observation
############################################################
output = "./space/"
try:
    os.stat(output)
except:
    if not os.path.isdir(output):
        os.makedirs(output)

# 観測天体の画像(Object : Image（.fits,.h5,.txt,.uvfitsなど、各ファイルのロードはチェック） or Movie)
image_86 = eh.image.load_image("./data_files/M87_86GHz.fits")
image_230 = eh.image.load_image("./data_files/M87_230GHz.fits")
############################################################
# observation specs
source = "M87"
srcloc = astropy.coordinates.SkyCoord.from_name(source)
RA = srcloc.ra.deg / 15
DEC = srcloc.dec.deg

hi_freq = 230  # 高い観測周波数[GHz]
low_freq = 86  # 低い観測周波数[GHz]　ただし、settingsには一つの周波数を選択
bandwidth = 8.0  # フリンジ検出帯域幅[GHz]

day = "15"  # day of the month for the observation
month = "Mar"  # month of observation; uses three-letter abbreviations
year = "2025"  # year of observation

t_start = 0  # 観測開始時間[h]
dt = 24  # トータルの観測時間[h]
t_int = 300  # 観測で積分する時間[s]
t_rest = 3600  # 次の積分までの間隔[s]

# fringe finding scheme; options are:
# ['fringegroups', [strong baseline SNR threshold, strong baseline coherence time [s]]
# 高 SNR の「強い基線」だけでフリンジを見つけ、その結果を使って 他の基線に位相・遅延の情報を伝播させる方式

# ['fpt', [strong baseline SNR threshold, strong baseline coherence time (in seconds),
# fpt reference frequency (in GHz), path to FPT reference model]
# 例['fpt', [8.0, 60.0, 86.0, "model_86GHz.fits"]]
# 低周波 86GHz の SNR>8 の基線で位相を求める
# coherence time 60秒でフィルタリング
# その位相を高周波 (例えば 230GHz)
# 最後に model_86GHz の visibility を参照して residual を最小化
fringe_finder_nofpt = ["fringegroups", [5, 10.0]]
fpt_threshold_basefac = 5
fpt_threshold = fpt_threshold_basefac * hi_freq / low_freq
print("FPT Threshold SNR is :" + str(fpt_threshold))
fringe_finder_fpt = ["fpt", [fpt_threshold, 10.0, low_freq, image_86]]


############################################################
# array specs
sites = [
    "ALMA",
    "APEX",
    "IRAM",
    "JCMT",
    "GBT",
    "IRK",
    "ISG",
    "MIZ",
    "SMA",
    "SMT",
    "KVNPC",
    "KVNYS",
    "NOEMA",
    "SPT",
    "space",
    "AMT",
    "GLT",
]  # 観測局
############################################################
# other settings

weather = "good"  # 天候情報 ('random', 'exact', 'good', 'typical', or 'poor')
ttype = "nfft"  # フーリエ変換の方法 ('direct', 'nfft', or 'fast')
random_seed = 12345  # 乱数シード。空白または None の場合は自動生成される。

# initialize the observation generator
custom_receivers = {
    "Low": {"lo": 84.0, "hi": 90.0, "T_R": 50.0, "SSR": 0.5},
    "Hi": {"lo": 220.0, "hi": 240.0, "T_R": 50.0, "SSR": 0.5},
}
T_R_overrides = {"space": {"Low": 30.0, "Hi": 25.0 * 2}}
# Spaceの情報
space_dish_diameter = 4
surface = 100  # microns
surf_rms_overrides = {
    "space": surface * 1.0e-6,
}
ephemeris = "./ephemeris/sekido"
D_overrides = {"space": space_dish_diameter}
# LowとHiのみを必ず作る
receiver_configuration_overrides = {
    "ALMA": ["Low", "Hi"],
    "APEX": ["Low", "Hi"],
    "IRAM": ["Low", "Hi"],
    "JCMT": ["Low", "Hi"],
    "NOB": ["Hi"],
    "IRK": ["Low"],
    "ISG": ["Low"],
    "MIZ": ["Low"],
    "KVNPC": ["Low", "Hi"],
    "KVNYS": ["Hi"],
    "SPT": ["Low", "Hi"],
    "SMT": ["Low", "Hi"],
    "SMA": ["Low", "Hi"],
    "AMT": ["Low", "Hi"],
    "GLT": ["Low", "Hi"],
    "space": ["Low", "Hi"],
}
# no fpt
frequency = hi_freq
fringe_finder = fringe_finder_nofpt
settings = {
    "model_file": image_230,
    "source": source,
    "RA": RA,
    "DEC": DEC,
    "sites": sites,
    "frequency": frequency,
    "bandwidth": bandwidth,
    "day": day,
    "month": month,
    "year": year,
    "t_start": t_start,
    "dt": dt,
    "t_int": t_int,
    "t_rest": t_rest,
    "fringe_finder": fringe_finder,
    "ttype": ttype,
    "random_seed": random_seed,
    "weather": weather,
}

obsgen = og.obs_generator(
    settings=settings,
    custom_receivers=custom_receivers,
    receiver_configuration_overrides=receiver_configuration_overrides,
    ephem=ephemeris,
    surf_rms_overrides=surf_rms_overrides,
    D_overrides=D_overrides,
    T_R_overrides=T_R_overrides,
    verbosity=0,
)

# generate the observation
obs = obsgen.make_obs(
    addgains=True,
    flagday=True,
    flagsun=True,
)

# save it as a uvfits file
obs.save_uvfits(output + "space.uvfits")

# fpt
frequency = hi_freq
fringe_finder = fringe_finder_fpt
settings = {
    "model_file": image_230,
    "source": source,
    "RA": RA,
    "DEC": DEC,
    "sites": sites,
    "frequency": frequency,
    "bandwidth": bandwidth,
    "day": day,
    "month": month,
    "year": year,
    "t_start": t_start,
    "dt": dt,
    "t_int": t_int,
    "t_rest": t_rest,
    "fringe_finder": fringe_finder,
    "ttype": ttype,
    "random_seed": random_seed,
    "weather": weather,
}

obsgen = og.obs_generator(
    settings=settings,
    custom_receivers=custom_receivers,
    receiver_configuration_overrides=receiver_configuration_overrides,
    surf_rms_overrides=surf_rms_overrides,
    ephem=ephemeris,
    D_overrides=D_overrides,
    T_R_overrides=T_R_overrides,
    verbosity=0,
)

# generate the observation
obs = obsgen.make_obs(
    addgains=True,
    flagday=True,
    flagsun=True,
)

# save it as a uvfits file
obs.save_uvfits(output + "fpt_space.uvfits")
