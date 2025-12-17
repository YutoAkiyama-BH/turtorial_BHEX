#######################################################
# imports
import ngehtsim.obs.obs_generator as og
import ehtim as eh
import astropy
import os

#######################################################
# generate an observation
############################################################
output = "./one_freq/"
try:
    os.stat(output)
except:
    if not os.path.isdir(output):
        os.makedirs(output)
# 観測天体の画像(Object : Image（.fits,.h5,.txt,.uvfitsなど、各ファイルのロードはチェック） or Movie)
image = eh.image.load_image("./data_files/M87_86GHz.fits")
############################################################
# observation specs
source = "M87"
srcloc = astropy.coordinates.SkyCoord.from_name(source)
RA = srcloc.ra.deg / 15
DEC = srcloc.dec.deg

frequency = 86  # 観測周波数[GHz]
bandwidth = 2.0  # フリンジ検出帯域幅[GHz]

day = "15"  # day of the month for the observation
month = "Apr"  # month of observation; uses three-letter abbreviations
year = "2025"  # year of observation

t_start = 0  # 観測開始時間[h]
dt = 24  # トータルの観測時間[h]
t_int = 300  # 観測で積分する時間[s]
t_rest = 600  # 次の積分までの間隔[s]

# fringe finding scheme; options are:
# ['fringegroups', [strong baseline SNR threshold, strong baseline coherence time (in seconds)]
# 高 SNR の「強い基線」だけでフリンジを見つけ、その結果を使って 他の基線に位相・遅延の情報を伝播させる方式
fringe_finder = ["fringegroups", [5.0, 10.0]]

############################################################
# array specs
# D_new = 10.0  # Telescope_Site_Matrix.csvに表記されていないアンテナ口径、統一されてしまうので注意[m]
sites = [
    "ALMA",
    "IRAM",
    "JCMT",
    "GBT",
    "IRK",
    "ISG",
    "KVNPC",
    "KVNTN",
]  # 観測局
############################################################
# other settings

weather = "good"  # 天候情報 ('random', 'exact', 'good', 'typical', or 'poor')
ttype = "nfft"  # フーリエ変換の方法 ('direct', 'nfft', or 'fast')
random_seed = 12345  # 乱数シード。空白または None の場合は自動生成される。

# settingsは基本的に
settings = {
    "model_file": image,
    "source": source,
    "RA": RA,
    "DEC": DEC,
    "sites": sites,
    # "D_new": D_new,
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

# initialize the observation generator
obsgen = og.obs_generator(settings=settings)
obs = obsgen.make_obs()
obs.save_uvfits(output + "one_freq.uvfits")

receiver_configuration_overrides = dict()
# SSRはSideband Separation Ratio（サイドバンド分離比）
# 高周波　SSR : 10–15 dB
# 低周波　SSR : 5–10 dB
custom_receivers = {"86GHz": {"lo": 82.0, "hi": 90.0, "T_R": 10, "SSR": 0.01}}
test_array_rec = {
    "ALMA": ["86GHz"],
    "IRAM": ["86GHz"],
    "JCMT": ["86GHz"],
    "GBT": ["86GHz"],
    "IRK": ["86GHz"],
    "ISG": ["86GHz"],
    "KVNPC": ["86GHz"],
    "KVNTN": ["86GHz"],
}
receiver_configuration_overrides.update(test_array_rec)
obsgen = og.obs_generator(
    settings=settings,
    custom_receivers=custom_receivers,
    receiver_configuration_overrides=receiver_configuration_overrides,
)
obs = obsgen.make_obs()
obs.save_uvfits(output + "rec_one_freq.uvfits")
