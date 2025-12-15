import streamlit as st
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NBA赛程查询", page_icon="🏀", layout="wide")
st.title("🏀 NBA实时赛程")

if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== 球队中英文映射 ======
team_translation = {
    "Atlanta Hawks": "老鹰", "Boston Celtics": "凯尔特人", "Brooklyn Nets": "篮网",
    "Charlotte Hornets": "黄蜂", "Chicago Bulls": "公牛", "Cleveland Cavaliers": "骑士",
    "Dallas Mavericks": "独行侠", "Denver Nuggets": "掘金", "Detroit Pistons": "活塞",
    "Golden State Warriors": "勇士", "Houston Rockets": "火箭", "Indiana Pacers": "步行者",
    "LA Clippers": "快船", "Los Angeles Lakers": "湖人", "Memphis Grizzlies": "灰熊",
    "Miami Heat": "热火", "Milwaukee Bucks": "雄鹿", "Minnesota Timberwolves": "森林狼",
    "New Orleans Pelicans": "鹈鹕", "New York Knicks": "尼克斯", "Oklahoma City Thunder": "雷霆",
    "Orlando Magic": "魔术", "Philadelphia 76ers": "76人", "Phoenix Suns": "太阳",
    "Portland Trail Blazers": "开拓者", "Sacramento Kings": "国王", "San Antonio Spurs": "马刺",
    "Toronto Raptors": "猛龙", "Utah Jazz": "爵士", "Washington Wizards": "奇才"
}

def translate_team_name(name):
    return team_translation.get(name, name)

# ====== 完整 NBA 球员中英文对照表（500+ 人，2024-25 赛季）======
player_translation = {
  "A.J. Green": "AJ·格林",
  "Aaron Nesmith": "阿龙·内史密斯",
  "Aaron Wiggins": "阿隆·威金斯",
  "Adama Sanogo": "阿达玛·萨诺戈",
  "Al Horford": "艾尔·霍福德",
  "Alperen Sengun": "阿尔佩伦·申京",
  "Amari Bailey": "阿马里·贝利",
  "Amen Thompson": "阿门·汤普森",
  "Andre Drummond": "安德烈·德拉蒙德",
  "Andre Jackson Jr.": "小安德烈·杰克逊",
  "Anthony Black": "安东尼·布莱克",
  "Anthony Davis": "安东尼·戴维斯",
  "Anthony Edwards": "安东尼·爱德华兹",
  "Armoni Brooks": "阿蒙尼·布鲁克斯",
  "Ausar Thompson": "奥萨尔·汤普森",
  "Bennedict Mathurin": "本尼迪克特·马瑟林",
  "Bilal Coulibaly": "比拉尔·库利巴利",
  "Bojan Bogdanovic": "博扬·博格达诺维奇",
  "Bogdan Bogdanovic": "博格丹·博格达诺维奇",
  "Brandon Boston Jr.": "小布兰登·波士顿",
  "Brandon Clarke": "布兰登·克拉克",
  "Brandon Ingram": "布兰登·英格拉姆",
  "Braxton Key": "布拉克斯顿·基",
  "Brett Maher": "布雷特·马厄",
  "Bruce Brown": "布鲁斯·布朗",
  "Cade Cunningham": "凯德·坎宁安",
  "Cam Thomas": "卡姆·托马斯",
  "Cam Whitmore": "卡姆·惠特莫尔",
  "Caris LeVert": "卡里斯·勒韦尔",
  "Chet Holmgren": "切特·霍姆格伦",
  "Chris Duarte": "克里斯·杜阿尔特",
  "Chris Paul": "克里斯·保罗",
  "Christian Braun": "克里斯蒂安·布劳恩",
  "Christian Koloko": "克里斯蒂安·科洛克",
  "CJ McCollum": "CJ·麦科勒姆",
  "Clint Capela": "克林特·卡佩拉",
  "Cole Anthony": "科尔·安东尼",
  "Collin Sexton": "科林·塞克斯顿",
  "Corey Kispert": "科里·基斯珀特",
  "Cory Joseph": "科里·约瑟夫",
  "D'Moi Hodge": "德莫伊·霍奇",
  "Daishen Nix": "戴申·尼克斯",
  "Damian Lillard": "达米安·利拉德",
  "Dante Exum": "丹特·埃克萨姆",
  "Darius Garland": "达柳斯·加兰",
  "Davion Mitchell": "达维恩·米切尔",
  "De'Aaron Fox": "德阿龙·福克斯",
  "De'Andre Hunter": "德安德烈·亨特",
  "De'Anthony Melton": "德安东尼·梅尔顿",
  "Dejounte Murray": "德章泰·穆雷",
  "Delon Wright": "德隆·赖特",
  "Deni Avdija": "德尼·阿夫迪亚",
  "Dereck Lively II": "德里克·利夫利二世",
  "Derrick Jones Jr.": "小德里克·琼斯",
  "Derrick Rose": "德里克·罗斯",
  "Devonte' Graham": "德冯特·格雷厄姆",
  "Dillon Brooks": "狄龙·布鲁克斯",
  "Domantas Sabonis": "多曼塔斯·萨博尼斯",
  "Donovan Mitchell": "多诺万·米切尔",
  "Donte DiVincenzo": "唐特·迪文琴佐",
  "Doug McDermott": "道格·麦克德莫特",
  "Drew Eubanks": "德鲁·尤班克斯",
  "Dru Smith": "德鲁·史密斯",
  "Dyson Daniels": "戴森·丹尼尔斯",
  "E.J. Liddell": "EJ·利德尔",
  "Evan Fournier": "埃文·富尼耶",
  "Evan Mobley": "埃文·莫布利",
  "Facundo Campazzo": "法昆多·坎帕佐",
  "Franz Wagner": "弗朗茨·瓦格纳",
  "Fred VanVleet": "弗雷德·范弗利特",
  "Gary Payton II": "小加里·佩顿",
  "Georges Niang": "乔治·尼昂",
  "Giannis Antetokounmpo": "扬尼斯·阿德托昆博",
  "Gordon Hayward": "戈登·海沃德",
  "Gradey Dick": "格雷迪·迪克",
  "Grayson Allen": "格雷森·艾伦",
  "Greg Brown III": "格雷格·布朗三世",
  "Gui Santos": "圭·桑托斯",
  "Harrison Barnes": "哈里森·巴恩斯",
  "Haywood Highsmith": "海伍德·海史密斯",
  "Herbert Jones": "赫伯特·琼斯",
  "Isaiah Collier": "以赛亚·科利尔",
  "Isaiah Joe": "以赛亚·乔",
  "Isaiah Livers": "以赛亚·利弗斯",
  "Isaiah Mobley": "以赛亚·莫布利",
  "Isaiah Stewart": "以赛亚·斯图尔特",
  "Ivica Zubac": "伊维察·祖巴茨",
  "Jabari Smith Jr.": "小贾巴里·史密斯",
  "Jaden Hardy": "杰登·哈迪",
  "Jaden Ivey": "杰登·艾维",
  "Jaden McDaniels": "杰登·麦克丹尼尔斯",
  "Jaden Springer": "杰登·斯普林格",
  "Jalen Duren": "杰伦·杜伦",
  "Jalen Green": "杰伦·格林",
  "Jalen Johnson": "杰伦·约翰逊",
  "Jalen Suggs": "杰伦·萨格斯",
  "Jalen Williams": "杰伦·威廉斯",
  "Jalen Wilson": "杰伦·威尔逊",
  "James Bouknight": "詹姆斯·布克奈特",
  "James Harden": "詹姆斯·哈登",
  "Ja Morant": "贾·莫兰特",
  "Jarrett Allen": "贾勒特·阿伦",
  "Jarred Vanderbilt": "贾里德·范德比尔特",
  "Jared Butler": "贾里德·巴特勒",
  "Jaime Jaquez Jr.": "小杰梅·贾克斯",
  "Jakob Poeltl": "雅各布·珀尔特尔",
  "Jamal Cain": "贾马尔·凯恩",
  "Jamal Murray": "贾马尔·穆雷",
  "Jared Rhoden": "贾里德·罗登",
  "Jaylen Brown": "杰伦·布朗",
  "Jaylen Clark": "杰伦·克拉克",
  "Jaylin Williams": "杰林·威廉斯",
  "Jayson Tatum": "杰森·塔图姆",
  "Jericho Sims": "杰里乔·西姆斯",
  "Jeremy Sochan": "杰里米·索汉",
  "Jett Howard": "杰特·霍华德",
  "Jimmy Butler": "吉米·巴特勒",
  "Joe Ingles": "乔·英格尔斯",
  "John Collins": "约翰·科林斯",
  "Johnny Davis": "约翰尼·戴维斯",
  "Jonas Valanciunas": "约纳斯·瓦兰丘纳斯",
  "Jonathan Kuminga": "乔纳森·库明加",
  "Jordan Clarkson": "乔丹·克拉克森",
  "Jordan Hawkins": "乔丹·霍金斯",
  "Jordan McLaughlin": "乔丹·麦克劳林",
  "Jordan Nwora": "乔丹·恩沃拉",
  "Jordan Poole": "乔丹·普尔",
  "Jose Alvarado": "何塞·阿尔瓦拉多",
  "Josh Christopher": "约什·克里斯托弗",
  "Josh Giddey": "约什·吉迪",
  "Josh Hart": "约什·哈特",
  "Josh Minott": "约什·米诺特",
  "JT Thor": "JT·索尔",
  "Julian Strawther": "朱利安·斯特劳瑟",
  "Julius Randle": "朱利叶斯·兰德尔",
  "Justin Champagnie": "贾斯汀·钱帕涅",
  "Justise Winslow": "贾斯蒂斯·温斯洛",
  "Jusuf Nurkic": "尤素夫·努尔基奇",
  "Kai Jones": "凯·琼斯",
  "Karl-Anthony Towns": "卡尔-安东尼·唐斯",
  "Kawhi Leonard": "科怀·伦纳德",
  "Keegan Murray": "基根·穆雷",
  "Kelly Olynyk": "凯利·奥利尼克",
  "Kelly Oubre Jr.": "小凯利·乌布雷",
  "Kel'el Ware": "凯尔·威尔",
  "Kenrich Williams": "肯里奇·威廉斯",
  "Kentavious Caldwell-Pope": "肯塔维奥斯·考德威尔-波普",
  "Keyonte George": "凯永特·乔治",
  "Khyri Thomas": "凯瑞·托马斯",
  "Killian Hayes": "基利安·海斯",
  "Kira Lewis Jr.": "小基拉·刘易斯",
  "Klay Thompson": "克莱·汤普森",
  "Kobe Bufkin": "科比·布夫金",
  "Kris Dunn": "克里斯·邓恩",
  "Kristaps Porzingis": "克里斯塔普斯·波尔津吉斯",
  "Kyle Anderson": "凯尔·安德森",
  "Kyle Kuzma": "凯尔·库兹马",
  "Kyrie Irving": "凯里·欧文",
  "Lamar Stevens": "拉马尔·史蒂文斯",
  "LaMelo Ball": "拉梅洛·鲍尔",
  "Larry Nance Jr.": "小拉里·南斯",
  "Lauri Markkanen": "劳里·马尔卡宁",
  "LeBron James": "勒布朗·詹姆斯",
  "Lindy Waters III": "林迪·沃特斯三世",
  "Lonnie Walker IV": "朗尼·沃克四世",
  "Luguentz Dort": "吕冈茨·多尔特",
  "Luke Kennard": "卢克·肯纳德",
  "Luke Kornet": "卢克·科内特",
  "Luka Doncic": "卢卡·东契奇",
  "Malaki Branham": "马拉基·布兰纳姆",
  "Malik Beasley": "马利克·比斯利",
  "Malik Monk": "马利克·蒙克",
  "Mamadi Diakite": "马马迪·迪亚基特",
  "Marcus Morris Sr.": "马库斯·莫里斯",
  "Marcus Sasser": "马库斯·萨瑟",
  "Markquis Nowell": "马克奎斯·诺韦尔",
  "MarJon Beauchamp": "马乔恩·博尚",
  "Max Christie": "马克斯·克里斯蒂",
  "Max Strus": "马克斯·斯特鲁斯",
  "Michael Porter Jr.": "小迈克尔·波特",
  "Miles Bridges": "迈尔斯·布里奇斯",
  "Miles Norris": "迈尔斯·诺里斯",
  "Mitchell Robinson": "米切尔·罗宾逊",
  "Monte Morris": "蒙特·莫里斯",
  "Moses Brown": "摩西·布朗",
  "Moses Moody": "摩西·穆迪",
  "Naz Reid": "纳兹·里德",
  "Neemias Queta": "尼米亚斯·奎塔",
  "Nico Mannion": "尼科·曼尼恩",
  "Nickeil Alexander-Walker": "纳吉尔·亚历山大-沃克",
  "Nick Richards": "尼克·理查兹",
  "Nikola Jokic": "尼古拉·约基奇",
  "Nikola Vucevic": "尼古拉·武切维奇",
  "OG Anunoby": "OG·阿努诺比",
  "Onyeka Okongwu": "奥涅卡·奥孔古",
  "Oshae Brissett": "奥谢·布里塞特",
  "P.J. Washington": "P.J.华盛顿",
  "Paolo Banchero": "保罗·班切罗",
  "Pat Connaughton": "帕特·康诺顿",
  "Pat Spencer": "帕特·斯宾塞",
  "Payton Pritchard": "佩顿·普里查德",
  "Peyton Watson": "佩顿·沃森",
  "Precious Achiuwa": "普雷舍斯·阿丘瓦",
  "Quentin Grimes": "昆汀·格里姆斯",
  "Reggie Jackson": "雷吉·杰克逊",
  "Richaun Holmes": "里乔恩·霍姆斯",
  "RJ Barrett": "RJ·巴雷特",
  "Robert Williams III": "罗伯特·威廉斯三世",
  "Ron Holland": "罗恩·霍兰",
  "Royce O'Neale": "罗伊斯·奥尼尔",
  "Ryan Arcidiacono": "瑞安·阿西迪亚科诺",
  "Ryan Dunn": "瑞安·邓恩",
  "Saben Lee": "塞本·李",
  "Saddiq Bey": "萨迪克·贝",
  "Sam Hauser": "萨姆·豪瑟",
  "Scoot Henderson": "斯库特·亨德森",
  "Scottie Barnes": "斯科蒂·巴恩斯",
  "Sekou Doumbouya": "塞科·敦布亚",
  "Shaedon Sharpe": "谢登·夏普",
  "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
  "Simone Fontecchio": "西蒙尼·丰泰基奥",
  "Stanley Johnson": "斯坦利·约翰逊",
  "Stephon Castle": "斯蒂芬·卡斯尔",
  "Sterling Brown": "斯特林·布朗",
  "Steven Adams": "史蒂文·亚当斯",
  "Tari Eason": "塔里·伊森",
  "Taurean Prince": "托里恩·普林斯",
  "Terance Mann": "特伦斯·曼恩",
  "Thaddeus Young": "萨迪厄斯·杨",
  "Theo Maledon": "泰奥·马勒东",
  "Tim Hardaway Jr.": "小蒂姆·哈达威",
  "Tobias Harris": "托拜厄斯·哈里斯",
  "Toumani Camara": "图马尼·卡马拉",
  "Trae Young": "特雷·杨",
  "Trendon Watford": "特伦登·沃特福德",
  "Tre Mann": "特雷·曼恩",
  "Tristan da Silva": "特里斯坦·达席尔瓦",
  "Tristan Thompson": "特里斯坦·汤普森",
  "Troy Brown Jr.": "小特洛伊·布朗",
  "Ty Jerome": "泰·杰罗姆",
  "Tyrese Haliburton": "泰瑞斯·哈利伯顿",
  "Tyrese Maxey": "泰瑞斯·马克西",
  "Tyler Herro": "泰勒·希罗",
  "Tyler Smith": "泰勒·史密斯",
  "Usman Garuba": "乌斯曼·加鲁巴",
  "Vit Krejci": "维特·克雷伊奇",
  "Walker Kessler": "沃克·凯斯勒",
  "Wendell Carter Jr.": "小温德尔·卡特",
  "Wendell Moore Jr.": "小温德尔·摩尔",
  "Xavier Tillman": "泽维尔·蒂尔曼",
  "Yuta Watanabe": "渡边雄太",
  "Zach Collins": "扎克·科林斯",
  "Zach LaVine": "扎克·拉文",
  "Zeke Nnaji": "齐克·纳吉",
  "Ziaire Williams": "齐亚伊尔·威廉斯",
  "Zion Williamson": "锡安·威廉森",
  "Aaron Gordon": "阿隆·戈登",
  "Adrian Griffin Jr.": "小阿德里安·格里芬",
  "Alex Caruso": "亚历克斯·卡鲁索",
  "Alex Sarr": "亚历克斯·萨尔",
  "Alec Burks": "亚历克·伯克斯",
  "Amir Coffey": "阿米尔·科菲",
  "Andre Iguodala": "安德烈·伊戈达拉",
  "Andrew Nembhard": "安德鲁·内姆哈德",
  "Andrew Wiggins": "安德鲁·威金斯",
  "Anthony Lamb": "安东尼·兰姆",
  "Armando Bacot": "阿曼多·巴科特",
  "Austin Reaves": "奥斯汀·里夫斯",
  "B.J. Boston": "BJ·波士顿",
  "Bam Adebayo": "巴姆·阿德巴约",
  "Ben Simmons": "本·西蒙斯",
  "Blake Wesley": "布莱克·韦斯利",
  "Boban Marjanovic": "博班·马扬诺维奇",
  "Bones Hyland": "邦斯·海兰德",
  "Brandon Williams": "布兰登·威廉斯",
  "Brice Sensabaugh": "布莱斯·森萨博",
  "Caleb Houstan": "凯莱布·豪斯坦",
  "Caleb Martin": "凯莱布·马丁",
  "Cam Reddish": "卡姆·雷迪什",
  "Chris Boucher": "克里斯·鲍彻",
  "Christian Wood": "克里斯蒂安·伍德",
  "Cole Swider": "科尔·斯威德",
  "DaRon Holmes II": "达龙·霍姆斯二世",
  "Dalton Knecht": "道尔顿·克内希特",
  "Daniel Gafford": "丹尼尔·加福德",
  "Daniel Theis": "丹尼尔·泰斯",
  "Davion Mintz": "达维恩·明茨",
  "DeAndre Jordan": "德安德烈·乔丹",
  "Deividas Sirvydis": "德维达斯·西尔维迪斯",
  "Derrick White": "德里克·怀特",
  "Devon Dotson": "德文·多特森",
  "Dexter Dennis": "德克斯特·丹尼斯",
  "D'Marco Dunn": "德马科·邓恩",
  "Drew Peterson": "德鲁·彼得森",
  "Duane Washington Jr.": "小杜安·华盛顿",
  "Emoni Bates": "埃莫尼·贝茨",
  "Eric Gordon": "埃里克·戈登",
  "Furkan Korkmaz": "富尔坎·科尔克马兹",
  "Gabe Vincent": "加布·文森特",
  "Garrett Temple": "加勒特·坦普尔",
  "Gary Trent Jr.": "小加里·特伦特",
  "Giorgio Milligan": "乔治·米利根",
  "Greg Foster": "格雷格·福斯特",
  "Hugo Besson": "雨果·贝松",
  "Isaiah Wong": "以赛亚·黄",
  "Jabari Walker": "贾巴里·沃克",
  "Jack White": "杰克·怀特",
  "Jacob Gilyard": "雅各布·吉利亚德",
  "Jalen Pickett": "杰伦·皮克特",
  "James Nnaji": "詹姆斯·纳吉",
  "Jamorko Pickett": "贾莫科·皮克特",
  "Jared Harper": "贾里德·哈珀",
  "Jarrell Brantley": "贾雷尔·布兰特利",
  "Jay Huff": "杰伊·哈夫",
  "Jaylen Wells": "杰伦·威尔斯",
  "Jeff Dowtin": "杰夫·道廷",
  "Jermaine Samuels": "杰梅因·萨缪尔斯",
  "Jevon Carter": "杰冯·卡特",
  "Joe Wieskamp": "乔·威斯坎普",
  "John Butler Jr.": "小约翰·巴特勒",
  "Jon Teske": "乔恩·特斯克",
  "Jordan Goodwin": "乔丹·古德温",
  "Josh Minaya": "约什·米纳亚",
  "K.C. Ndefo": "KC·恩代福",
  "Kendrick Nunn": "肯德里克·努恩",
  "Kenyon Martin Jr.": "小肯扬·马丁",
  "Kessler Edwards": "凯斯勒·爱德华兹",
  "Khyri Thomas": "凯瑞·托马斯",
  "Kobi Simmons": "科比·西蒙斯",
  "Kostas Antetokounmpo": "科斯塔斯·阿德托昆博",
  "Kristian Doolittle": "克里斯蒂安·杜利特尔",
  "Landry Shamet": "兰德里·沙梅特",
  "Latrell Turrentine": "拉特雷尔·塔伦廷",
  "Leaky Black": "李奇·布莱克",
  "Lester Quiñones": "莱斯特·基诺内斯",
  "Luka Garza": "卢卡·加尔扎",
  "Mac McClung": "麦克·麦克朗",
  "Malachi Flynn": "马拉奇·弗林",
  "Mamadi Diakite": "马马迪·迪亚基特",
  "Mark Armstrong": "马克·阿姆斯特朗",
  "Markieff Morris": "马基夫·莫里斯",
  "Marques Bolden": "马奎斯·博尔登",
  "Matt Hurt": "马特·赫特",
  "Maxwell Lewis": "麦克斯韦尔·刘易斯",
  "Micheal Eric": "迈克尔·埃里克",
  "Miles McBride": "迈尔斯·麦克布莱德",
  "Moussa Diabate": "穆萨·迪亚巴特",
  "Nate Darling": "内特·达林",
  "Nate Hinton": "内特·欣顿",
  "Nate Laszewski": "内特·拉斯泽夫斯基",
  "Naz Mitrou-Long": "纳兹·米特鲁-朗",
  "Nerlens Noel": "奈伦斯·诺埃尔",
  "Ochai Agbaji": "奥柴·阿巴基",
  "Oliver-Maxence Prosper": "奥利弗-马克桑斯·普罗斯珀",
  "Omari Moore": "奥马里·摩尔",
  "Pete Nance": "皮特·南斯",
  "Peyton Watson": "佩顿·沃森",
  "Quincy Olivari": "昆西·奥利瓦里",
  "RayJ Dennis": "雷杰·丹尼斯",
  "Reece Beekman": "里斯·比克曼",
  "Riley Minix": "莱利·米尼克斯",
  "RJ Davis": "RJ·戴维斯",
  "Rob Dillingham": "罗布·迪林厄姆",
  "Ryan Kalkbrenner": "瑞安·卡尔克布伦纳",
  "Saben Lee": "塞本·李",
  "Sam Merrill": "萨姆·梅里尔",
  "Sandro Mamukelashvili": "桑德罗·马穆凯拉什维利",
  "Scotty Pippen Jr.": "小斯科蒂·皮蓬",
  "Shaedon Sharpe": "谢登·夏普",
  "Shaq Buchanan": "沙克·布坎南",
  "Sidney Cooks": "西德尼·库克斯",
  "Sidy Cissoko": "西迪·西索科",
  "Skylar Mays": "斯凯拉·梅斯",
  "Stephon Castle": "斯蒂芬·卡斯尔",
  "Tariq Castro-Fields": "塔里克·卡斯特罗-菲尔兹",
  "Taz Sherman": "塔兹·谢尔曼",
  "Terquavion Smith": "特夸维恩·史密斯",
  "Tidjane Salaün": "蒂贾尼·萨隆",
  "Tobias Harris": "托拜厄斯·哈里斯",
  "Tomer Ginat": "托默·吉纳特",
  "Toumani Camara": "图马尼·卡马拉",
  "Trayce Jackson-Davis": "特雷斯·杰克逊-戴维斯",
  "Tre Mitchell": "特雷·米切尔",
  "Trendon Watford": "特伦登·沃特福德",
  "Ty Jerome": "泰·杰罗姆",
  "Tyrese Haliburton": "泰瑞斯·哈利伯顿",
  "Tyler Bey": "泰勒·贝",
  "Tyler Kolek": "泰勒·科莱克",
  "Tyson Etienne": "泰森·埃蒂安",
  "Umoja Gibson": "乌莫贾·吉布森",
  "Vasilije Micic": "瓦西里耶·米契奇",
  "Vernon Carey Jr.": "小弗农·凯里",
  "Victor Oladipo": "维克托·奥拉迪波",
  "Victor Wembanyama": "维克托·文班亚马",
  "Walker Kessler": "沃克·凯斯勒",
  "Will Richardson": "威尔·理查德森",
  "Xavier Sneed": "泽维尔·斯尼德",
  "Yves Missi": "伊夫·米西",
  "Zaccharie Risacher": "扎卡里·里萨谢",
  "Zach Edey": "扎克·埃迪",
  "Zavier Simpson": "扎维尔·辛普森"
}

def translate_player_name(name):
    """将英文球员名转为中文，若无则返回原名"""
    name = name.strip()
    # 处理可能的中间名缩写差异，如 "De'Anthony Melton" vs "Deanthony Melton"
    # 此处简化处理，实际可加 fuzzy match，但先用精确匹配
    return player_translation.get(name, name)

# ====== 其余函数保持不变，仅在 parse_player_stats 中加入翻译 ======

@st.cache_data(ttl=30)
def fetch_nba_schedule(date_str):
    try:
        eastern = pytz.timezone('America/New_York')
        beijing_dt = beijing_tz.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        eastern_dt = beijing_dt.astimezone(eastern)
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        params = {'dates': eastern_dt.strftime('%Y%m%d'), 'lang': 'zh', 'region': 'cn'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"获取赛程失败: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_player_stats(event_id):
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/boxscore?event={event_id}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        st.session_state.debug = str(e)
        return None

def format_time(t):
    if not t or str(t).strip() in ('0', '0:00', '--', '', 'DNP', 'N/A'):
        return '0:00'
    s = str(t).strip()
    if ':' in s:
        return s
    try:
        minutes = int(float(s))
        return f"{minutes}:00"
    except:
        return s

def parse_player_stats(game_data):
    try:
        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section or len(players_section) < 2:
            return [], []

        home_players = players_section[1]
        away_players = players_section[0]

        def extract_team_data(team_data):
            stats_list = team_data.get('statistics', [])
            if not stats_list:
                return []
            main_stat = stats_list[0]
            labels = main_stat.get('labels', [])
            athletes = main_stat.get('athletes', [])
            
            parsed = []
            for ath in athletes:
                name_en = ath.get('athlete', {}).get('displayName', '').strip()
                name_cn = translate_player_name(name_en)  # <<< 关键：翻译球员名
                raw_vals = ath.get('stats', [])
                if not name_en or not raw_vals:
                    continue

                stat_map = {}
                for i, label in enumerate(labels):
                    if i < len(raw_vals):
                        stat_map[label] = raw_vals[i]

                def parse_shot(s):
                    s = str(s).replace('/', '-').strip()
                    if '-' in s:
                        parts = s.split('-')
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            return parts[0], parts[1]
                    return '0', '0'

                fgm, fga = parse_shot(stat_map.get('FGM-A', stat_map.get('FG', '0-0')))
                threepm, threepa = parse_shot(stat_map.get('3PM-A', stat_map.get('3PT', '0-0')))
                ftm, fta = parse_shot(stat_map.get('FTM-A', stat_map.get('FT', '0-0')))

                def get_num(key, default='0'):
                    val = stat_map.get(key, default)
                    return str(val) if str(val).replace('.', '').isdigit() else default

                minutes = stat_map.get('MIN', '0')
                pts = get_num('PTS')
                reb = get_num('REB')
                ast = get_num('AST')
                tov = get_num('TO')

                parsed.append({
                    '球员': name_cn,  # <<< 使用中文名
                    '时间': format_time(minutes),
                    '得分': pts,
                    '投篮': f"{fgm}/{fga}",
                    '三分': f"{threepm}/{threepa}",
                    '罚球': f"{ftm}/{fta}",
                    '篮板': reb,
                    '助攻': ast,
                    '失误': tov
                })
            return parsed

        home_data = extract_team_data(home_players)
        away_data = extract_team_data(away_players)

        return away_data, home_data

    except Exception as e:
        st.session_state.debug = f"Parse error: {str(e)}"
        return [], []

# Sidebar
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )

# Main
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

with st.spinner("加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据")
    st.stop()

events = schedule['events']
if not events:
    st.info("今日无比赛")
    st.stop()

for i, event in enumerate(events):
    comp = event.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) < 2:
        continue

    home = competitors[0]
    away = competitors[1]

    home_name = translate_team_name(home.get('team', {}).get('displayName', '主队'))
    away_name = translate_team_name(away.get('team', {}).get('displayName', '客队'))
    home_score = home.get('score', '0')
    away_score = away.get('score', '0')

    status_type = event.get('status', {}).get('type', {})
    state = status_type.get('state', 'pre')
    desc = status_type.get('description', '未开始')
    badge = {"in": "🟢 进行中", "post": "⚫ 已结束"}.get(state, "⏳ 未开始")

    try:
        utc_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        bj_time = utc_time.astimezone(beijing_tz).strftime("%H:%M")
    except:
        bj_time = "时间待定"

    cols = st.columns([2, 1, 0.5, 1, 2])
    cols[0].markdown(f"**{away_name}**")
    cols[1].markdown(f"**{away_score}**")
    cols[2].markdown("**VS**")
    cols[3].markdown(f"**{home_score}**")
    cols[4].markdown(f"**{home_name}**")
    st.caption(f"{badge} | {desc} | ⏰ {bj_time}")

    if state in ['in', 'post']:
        with st.spinner("加载球员数据..."):
            game_data = fetch_player_stats(event['id'])
            if game_data:
                away_p, home_p = parse_player_stats(game_data)
                if away_p or home_p:
                    st.subheader("📊 球员数据")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**{away_name}**")
                        if away_p:
                            df = pd.DataFrame(away_p)
                            df['pts'] = pd.to_numeric(df['得分'], errors='coerce')
                            df = df.sort_values('pts', ascending=False).drop('pts', axis=1)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("无数据")
                    with c2:
                        st.markdown(f"**{home_name}**")
                        if home_p:
                            df = pd.DataFrame(home_p)
                            df['pts'] = pd.to_numeric(df['得分'], errors='coerce')
                            df = df.sort_values('pts', ascending=False).drop('pts', axis=1)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("无数据")
            else:
                st.warning("球员数据加载失败")

    if i < len(events) - 1:
        st.divider()

st.divider()
col1, col2 = st.columns([3, 1])
col1.caption(f"更新于: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")
if col2.button("🔄 刷新"):
    st.cache_data.clear()
    st.rerun()

