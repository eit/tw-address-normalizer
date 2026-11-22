import pytest

from tw_address_normalizer import from_int, normalize, to_halfwidth, to_int


@pytest.mark.parametrize(
    "raw, want",
    [
        # full-width digits and spaces
        ("台北市內湖區堤頂大道二段４０９號7樓", "臺北市內湖區堤頂大道二段409號7樓"),
        ("臺北市 中山區 民族東路１７號", "臺北市中山區民族東路17號"),
        # 台 -> 臺 only in the county/city name
        ("台中市霧峰區柳豐路500號", "臺中市霧峰區柳豐路500號"),
        ("台東縣台東市中華路一段1號", "臺東縣台東市中華路一段1號"),
        ("彰化縣員林市三民東街210號", "彰化縣員林市三民東街210號"),
        # look-alike characters
        ("新北巿板橋區文化路一段1號", "新北市板橋區文化路一段1號"),
        ("臺南市新化鎭中正路1號", "臺南市新化鎮中正路1號"),
        ("臺北市内湖區成功路四段1號", "臺北市內湖區成功路四段1號"),
        # merged counties
        ("台北縣板橋市文化路1段1號", "新北市板橋區文化路一段1號"),
        ("桃園縣桃園市中正路1號", "桃園市桃園區中正路1號"),
        ("臺中縣大里市中興路二段1號", "臺中市大里區中興路二段1號"),
        ("高雄縣鳳山市光復路一段1號", "高雄市鳳山區光復路一段1號"),
        ("臺北縣烏來鄉烏來街1號", "新北市烏來區烏來街1號"),
        ("臺南縣", "臺南市"),
        # road sections in Chinese numerals
        ("臺北市信義路2段213號", "臺北市信義路二段213號"),
        ("臺中市臺灣大道10段1號", "臺中市臺灣大道十段1號"),
        ("某路12段1號", "某路十二段1號"),
        # lanes, alleys, numbers in Arabic numerals
        ("新北市中和區華新街一百零九巷十一弄三之二號", "新北市中和區華新街109巷11弄3之2號"),
        ("臺北市大安區和平東路二段一一八巷五衖七號", "臺北市大安區和平東路二段118巷5衖7號"),
        ("臺中市西區五權新一巷十號", "臺中市西區五權新一巷10號"),  # 新一巷 is a name, kept
        ("臺北市中正區八德路一段二十號之三", "臺北市中正區八德路一段20號之3"),
        # hyphens become 之
        ("臺北市中正區八德路一段5-1號", "臺北市中正區八德路一段5之1號"),
        ("臺北市中正區八德路一段5號3樓－2", "臺北市中正區八德路一段5號3樓之2"),
        # floors
        ("臺北市信義路二段213號10F", "臺北市信義路二段213號10樓"),
        ("臺北市信義路二段213號三F", "臺北市信義路二段213號3樓"),
        ("臺北市信義路二段213號十二樓之一", "臺北市信義路二段213號12樓之1"),
        ("臺北市信義路二段213號地下二樓", "臺北市信義路二段213號B2"),
        ("臺北市信義路二段213號B1F", "臺北市信義路二段213號B1"),
        ("臺中市霧峰區柳豐路500號(5F秘書室)", "臺中市霧峰區柳豐路500號(5樓秘書室)"),
        # leading postcode and country are kept / dropped
        ("114台灣台北市內湖區堤頂大道二段409號", "114臺北市內湖區堤頂大道二段409號"),
        ("臺灣省台中市西區民生路1號", "臺中市西區民生路1號"),
        # the README example
        ("台北縣板橋市文化路１段１００巷五弄十三-一號三F", "新北市板橋區文化路一段100巷5弄13之1號3樓"),
        # already clean input is unchanged
        ("臺北市大安區忠孝東路四段100號5樓", "臺北市大安區忠孝東路四段100號5樓"),
        ("", ""),
    ],
)
def test_normalize(raw, want):
    assert normalize(raw) == want


def test_idempotent():
    s = "台北縣板橋市文化路１段１００巷五弄十三-一號三F"
    assert normalize(normalize(s)) == normalize(s)


@pytest.mark.parametrize(
    "text, n",
    [
        ("一", 1), ("十", 10), ("十三", 13), ("二十", 20), ("二十一", 21),
        ("一百", 100), ("一百零五", 105), ("一百一十", 110), ("兩百", 200),
        ("一千零一", 1001), ("二一三", 213), ("〇五", 5),
    ],
)
def test_to_int(text, n):
    assert to_int(text) == n


@pytest.mark.parametrize(
    "n, text",
    [(1, "一"), (10, "十"), (12, "十二"), (20, "二十"), (105, "一百零五"), (110, "一百一十"), (1010, "一千零一十")],
)
def test_from_int(n, text):
    assert from_int(n) == text


def test_round_trip():
    for n in range(1, 10000):
        assert to_int(from_int(n)) == n


def test_bad_input():
    with pytest.raises(ValueError):
        to_int("三a")
    with pytest.raises(ValueError):
        from_int(0)


def test_halfwidth():
    assert to_halfwidth("１２３ＡＢＣ－　") == "123ABC- "


@pytest.mark.parametrize(
    "raw, want",
    [
        ("臺北市信義路二段213號6F之一", "臺北市信義路二段213號6樓之1"),
        ("臺北市信義路二段五之三之一號", "臺北市信義路二段5之3之1號"),
        ("台灣台灣台北市信義路二段1號", "臺北市信義路二段1號"),
        ("中華民國台灣省台中市西區民生路1號", "臺中市西區民生路1號"),
    ],
)
def test_found_on_real_data(raw, want):
    assert normalize(raw) == want
    assert normalize(want) == want
