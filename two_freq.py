#######################################################
# imports
import ngehtsim.obs.obs_generator as og
import ehtim as eh
import astropy
import os

#######################################################
# generate an observation
############################################################
output = "./two_freq/"
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

D_new = 9.0

hi_freq = 230  # 高い観測周波数[GHz]
low_freq = 86  # 低い観測周波数[GHz]　ただし、settingsには一つの周波数を選択
bandwidth = 8.0  # フリンジ検出帯域幅[GHz]

day = "15"  # day of the month for the observation
month = "Apr"  # month of observation; uses three-letter abbreviations
year = "2025"  # year of observation

t_start = 0  # 観測開始時間[h]
dt = 24  # トータルの観測時間[h]
t_int = 300  # 観測で積分する時間[s]
t_rest = 600  # 次の積分までの間隔[s]

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
fringe_finder_nofpt = ["fringegroups", [5.0, 10.0]]
fpt_threshold_basefac = 5.0
fpt_threshold = fpt_threshold_basefac * hi_freq / low_freq
print("FPT Threshold SNR is :" + str(fpt_threshold))
fringe_finder_fpt = ["fpt", [fpt_threshold, 10.0, low_freq, image_86]]


############################################################
# array specs
sites = [
    "ALMA",
    "IRAM",
    "JCMT",
    "GBT",
    "IRK",
    "ISG",
    "MIZ",
    "YAM",
    "KVNPC",
    "KVNTN",
    "KVNUS",
    "KVNYS",
]  # 観測局
############################################################
# other settings

weather = "good"  # 天候情報 ('random', 'exact', 'good', 'typical', or 'poor')
ttype = "nfft"  # フーリエ変換の方法 ('direct', 'nfft', or 'fast')
random_seed = 12345  # 乱数シード。空白または None の場合は自動生成される。

# initialize the observation generator
custom_receivers = {
    "Low": {"lo": 82.0, "hi": 90.0, "T_R": 50.0, "SSR": 5},
    "Hi": {"lo": 226.0, "hi": 234.0, "T_R": 50.0, "SSR": 10},
}
surf_rms_overrides = {
    "IRK": 25.0 * 1.0e-6,
    "ISG": 25.0 * 1.0e-6,
    "MIZ": 25.0 * 1.0e-6,
    "YAM": 100 * 1.0e-6,
}
# LowとHiのみを必ず作る
receiver_configuration_overrides = {
    "ALMA": ["Low", "Hi"],
    "IRAM": ["Low", "Hi"],
    "JCMT": ["Low", "Hi"],
    "GBT": ["Low"],
    "IRK": ["Low", "Hi"],
    "ISG": ["Low", "Hi"],
    "MIZ": ["Low", "Hi"],
    "YAM": ["Low", "Hi"],
    "KVNPC": ["Low", "Hi"],
    "KVNTN": ["Low", "Hi"],
    "KVNUS": ["Hi"],
    "KVNYS": ["Hi"],
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
    surf_rms_overrides=surf_rms_overrides,
    verbosity=0,
)

# generate the observation
obs = obsgen.make_obs()

# save it as a uvfits file
obs.save_uvfits(output + "two_freq.uvfits")


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
    verbosity=0,
)

# generate the observation
obs_fpt = obsgen.make_obs()

# save it as a uvfits file
obs_fpt.save_uvfits(output + "fpt_two_freq.uvfits")
