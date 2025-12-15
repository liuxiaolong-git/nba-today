
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
    "LeBron James": "勒布朗·詹姆斯",
    "Stephen Curry": "斯蒂芬·库里",
    "Kevin Durant": "凯文·杜兰特",
    "Giannis Antetokounmpo": "扬尼斯·阿德托昆博",
    "Joel Embiid": "乔尔·恩比德",
    "Nikola Jokic": "尼古拉·约基奇",
    "Luka Doncic": "卢卡·东契奇",
    "Jayson Tatum": "杰森·塔图姆",
    "Ja Morant": "贾·莫兰特",
    "Devin Booker": "德文·布克",
    "Damian Lillard": "达米安·利拉德",
    "Jimmy Butler": "吉米·巴特勒",
    "Kawhi Leonard": "科怀·伦纳德",
    "Anthony Davis": "安东尼·戴维斯",
    "Kyrie Irving": "凯里·欧文",
    "James Harden": "詹姆斯·哈登",
    "Russell Westbrook": "拉塞尔·威斯布鲁克",
    "Chris Paul": "克里斯·保罗",
    "Klay Thompson": "克莱·汤普森",
    "Draymond Green": "德雷蒙德·格林",
    "Paul George": "保罗·乔治",
    "Zion Williamson": "锡安·威廉森",
    "Trae Young": "特雷·杨",
    "Donovan Mitchell": "多诺万·米切尔",
    "Darius Garland": "达柳斯·加兰",
    "De'Aaron Fox": "德阿龙·福克斯",
    "Shai Gilgeous-Alexander": "谢伊·吉尔杰斯-亚历山大",
    "Anthony Edwards": "安东尼·爱德华兹",
    "LaMelo Ball": "拉梅洛·鲍尔",
    "Victor Wembanyama": "维克托·文班亚马",
    "Paolo Banchero": "保罗·班切罗",
    "Cade Cunningham": "凯德·坎宁安",
    "Jalen Suggs": "杰伦·萨格斯",
    "Evan Mobley": "埃文·莫布利",
    "Scottie Barnes": "斯科蒂·巴恩斯",
    "Franz Wagner": "弗朗茨·瓦格纳",
    "Chet Holmgren": "切特·霍姆格伦",
    "Jalen Williams": "杰伦·威廉姆斯 (雷霆)",
    "Brandon Ingram": "布兰登·英格拉姆",
    "DeMar DeRozan": "德玛尔·德罗赞",
    "Zach LaVine": "扎克·拉文",
    "Nikola Vucevic": "尼古拉·武切维奇",
    "Karl-Anthony Towns": "卡尔-安东尼·唐斯",
    "Rudy Gobert": "鲁迪·戈贝尔",
    "Mike Conley": "迈克·康利",
    "Jrue Holiday": "朱·霍勒迪",
    "Bam Adebayo": "巴姆·阿德巴约",
    "Tyler Herro": "泰勒·希罗",
    "Max Strus": "马克斯·斯特鲁斯",
    "CJ McCollum": "CJ·麦科勒姆",
    "Herbert Jones": "赫伯特·琼斯",
    "Jose Alvarado": "何塞·阿尔瓦拉多",
    "Larry Nance Jr.": "小拉里·南斯",
    "Dyson Daniels": "戴森·丹尼尔斯",
    "Trey Murphy III": "特雷·墨菲三世",
    "Jordan Hawkins": "乔丹·霍金斯",
    "Alex Caruso": "亚历克斯·卡鲁索",
    "Coby White": "科比·怀特",
    "Ayo Dosunmu": "阿约·多孙穆",
    "Torrey Craig": "托里·克雷格",
    "Jaden McDaniels": "杰登·麦克丹尼尔斯",
    "Nickeil Alexander-Walker": "纳吉尔·亚历山大-沃克",
    "Jordan McLaughlin": "乔丹·麦克劳林",
    "Naz Reid": "纳兹·里德",
    "Taurean Prince": "托里恩·普林斯",
    "Cam Reddish": "卡姆·雷迪什",
    "Dalton Knecht": "道尔顿·克内希特",
    "Bronny James": "布朗尼·詹姆斯",
    "D'Moi Hodge": "德莫伊·霍奇",
    "Austin Reaves": "奥斯汀·里夫斯",
    "D'Angelo Russell": "丹吉洛·拉塞尔",
    "Rui Hachimura": "八村垒",
    "Jarred Vanderbilt": "贾里德·范德比尔特",
    "Gabe Vincent": "加布·文森特",
    "Christian Wood": "克里斯蒂安·伍德",
    "Max Christie": "马克斯·克里斯蒂",
    "Jaxson Hayes": "杰克逊·海斯",
    "Andrew Wiggins": "安德鲁·威金斯",
    "Gary Payton II": "小加里·佩顿",
    "Moses Moody": "摩西·穆迪",
    "Brandin Podziemski": "布兰丁·波杰姆斯基",
    "Trayce Jackson-Davis": "特雷斯·杰克逊-戴维斯",
    "Lindy Waters III": "林迪·沃特斯三世",
    "Gui Santos": "圭·桑托斯",
    "Usman Garuba": "乌斯曼·加鲁巴",
    "Pat Spencer": "帕特·斯宾塞",
    "Kristaps Porzingis": "克里斯塔普斯·波尔津吉斯",
    "Derrick White": "德里克·怀特",
    "Al Horford": "艾尔·霍福德",
    "Sam Hauser": "萨姆·豪瑟",
    "Payton Pritchard": "佩顿·普里查德",
    "Luke Kornet": "卢克·科内特",
    "Oshae Brissett": "奥谢·布里塞特",
    "Neemias Queta": "尼米亚斯·奎塔",
    "Jamal Murray": "贾马尔·穆雷",
    "Michael Porter Jr.": "小迈克尔·波特",
    "Aaron Gordon": "阿隆·戈登",
    "Kentavious Caldwell-Pope": "肯塔维奥斯·考德威尔-波普",
    "Reggie Jackson": "雷吉·杰克逊",
    "Christian Braun": "克里斯蒂安·布劳恩",
    "Peyton Watson": "佩顿·沃森",
    "Zeke Nnaji": "齐克·纳吉",
    "Julian Strawther": "朱利安·斯特劳瑟",
    "P.J. Washington": "P.J.华盛顿",
    "Daniel Gafford": "丹尼尔·加福德",
    "Derrick Jones Jr.": "小德里克·琼斯",
    "Josh Green": "约什·格林",
    "Maxi Kleber": "马克西·克勒贝尔",
    "Dante Exum": "丹特·埃克萨姆",
    "Jaden Hardy": "杰登·哈迪",
    "Dwight Powell": "德怀特·鲍威尔",
    "Alec Burks": "亚历克·伯克斯",
    "Brook Lopez": "布鲁克·洛佩斯",
    "Bobby Portis": "鲍比·波蒂斯",
    "Khris Middleton": "克里斯·米德尔顿",
    "Pat Connaughton": "帕特·康诺顿",
    "Malik Beasley": "马利克·比斯利",
    "Jae Crowder": "杰·克劳德",
    "Andre Jackson Jr.": "小安德烈·杰克逊",
    "Thanasis Antetokounmpo": "萨纳西斯·阿德托昆博",
    "Tyrese Maxey": "泰瑞斯·马克西",
    "Tobias Harris": "托拜厄斯·哈里斯",
    "De'Anthony Melton": "德安东尼·梅尔顿",
    "Kelly Oubre Jr.": "小凯利·乌布雷",
    "Nicolas Batum": "尼古拉斯·巴图姆",
    "Caleb Martin": "凯莱布·马丁",
    "Eric Gordon": "埃里克·戈登",
    "Jaden Springer": "杰登·斯普林格",
    "Bradley Beal": "布拉德利·比尔",
    "Jusuf Nurkic": "尤素夫·努尔基奇",
    "Grayson Allen": "格雷森·艾伦",
    "Royce O'Neale": "罗伊斯·奥尼尔",
    "Bol Bol": "波尔·波尔",
    "Drew Eubanks": "德鲁·尤班克斯",
    "Ryan Dunn": "瑞安·邓恩",
    "Josh Giddey": "约什·吉迪",
    "Isaiah Joe": "以赛亚·乔",
    "Kenrich Williams": "肯里奇·威廉姆斯",
    "Aaron Wiggins": "阿隆·威金斯",
    "Cason Wallace": "卡森·华莱士",
    "Jaylin Williams": "杰林·威廉姆斯",
    "Gordon Hayward": "戈登·海沃德",
    "Norman Powell": "诺曼·鲍威尔",
    "Ivica Zubac": "伊维察·祖巴茨",
    "Terance Mann": "特伦斯·曼恩",
    "Amir Coffey": "阿米尔·科菲",
    "Kris Dunn": "克里斯·邓恩",
    "Daniel Theis": "丹尼尔·泰斯",
    "Moussa Diabate": "穆萨·迪亚巴特",
    "Dejounte Murray": "德章泰·穆雷",
    "De'Andre Hunter": "德安德烈·亨特",
    "Onyeka Okongwu": "奥涅卡·奥孔古",
    "Clint Capela": "克林特·卡佩拉",
    "Bogdan Bogdanovic": "博格丹·博格达诺维奇",
    "John Collins": "约翰·科林斯",
    "Jalen Johnson": "杰伦·约翰逊",
    "Saddiq Bey": "萨迪克·贝",
    "Malik Monk": "马利克·蒙克",
    "Domantas Sabonis": "多曼塔斯·萨博尼斯",
    "Keegan Murray": "基根·穆雷",
    "Davion Mitchell": "达维恩·米切尔",
    "Harrison Barnes": "哈里森·巴恩斯",
    "Jalen Green": "杰伦·格林",
    "Alperen Sengun": "阿尔佩伦·申京",
    "Jabari Smith Jr.": "小贾巴里·史密斯",
    "Fred VanVleet": "弗雷德·范弗利特",
    "Dillon Brooks": "狄龙·布鲁克斯",
    "Tari Eason": "塔里·伊森",
    "Amen Thompson": "阿门·汤普森",
    "Cam Whitmore": "卡姆·惠特莫尔",
    "Dereck Lively II": "德里克·利夫利二世",
    "Quentin Grimes": "昆汀·格里姆斯",
    "Precious Achiuwa": "普雷舍斯·阿丘瓦",
    "OG Anunoby": "OG·阿努诺比",
    "Bruce Brown": "布鲁斯·布朗",
    "Julius Randle": "朱利叶斯·兰德尔",
    "Jalen Brunson": "杰伦·布伦森",
    "Donte DiVincenzo": "唐特·迪文琴佐",
    "Mitchell Robinson": "米切尔·罗宾逊",
    "Josh Hart": "约什·哈特",
    "Cory Joseph": "科里·约瑟夫",
    "Isaiah Stewart": "以赛亚·斯图尔特",
    "Killian Hayes": "基利安·海斯",
    "Ausar Thompson": "奥萨尔·汤普森",
    "Jaden Ivey": "杰登·艾维",
    "Bojan Bogdanovic": "博扬·博格达诺维奇",
    "Kyle Kuzma": "凯尔·库兹马",
    "Deni Avdija": "德尼·阿夫迪亚",
    "Corey Kispert": "科里·基斯珀特",
    "Bilal Coulibaly": "比拉尔·库利巴利",
    "Jordan Poole": "乔丹·普尔",
    "Jonathan Kuminga": "乔纳森·库明加",
    "Ron Holland": "罗恩·霍兰",
    "Stephon Castle": "斯蒂芬·卡斯尔",
    "Alex Sarr": "亚历克斯·萨尔",
    "Reece Beekman": "里斯·比克曼",
    "Tidjane Salaün": "蒂贾尼·萨隆",
    "Harold Moukoudi": "哈罗德·穆昆迪",
    "Tyler Smith": "泰勒·史密斯",
    "Tristan da Silva": "特里斯坦·达席尔瓦",
    "Kel'el Ware": "凯尔·威尔",
    "Jaime Jaquez Jr.": "小海梅·哈克斯",
    "Keyonte George": "基扬特·乔治",
    "Walker Kessler": "沃克·凯斯勒",
    "Collin Sexton": "科林·塞克斯顿",
    "Simone Fontecchio": "西蒙尼·丰泰基奥",
    "Lauri Markkanen": "劳里·马尔卡宁",
    "Jordan Clarkson": "乔丹·克拉克森",
    "Kelly Olynyk": "凯利·奥利尼克",
    "Jared Butler": "贾里德·巴特勒",
    "Trey Jemison": "特雷·杰米森",
    "Braxton Key": "布拉克斯顿·基",
    "Isaiah Collier": "以赛亚·科利尔",
    "Nico Mannion": "尼科·曼尼恩",
    "Daishen Nix": "戴申·尼克斯",
    "Sidy Cissoko": "西迪·西索科",
    "Stanley Johnson": "斯坦利·约翰逊",
    "Justin Champagnie": "贾斯汀·钱帕涅",
    "Jalen Wilson": "杰伦·威尔逊",
    "Dru Smith": "德鲁·史密斯",
    "Marcus Sasser": "马库斯·萨瑟",
    "Gradey Dick": "格雷迪·迪克",
    "Scoot Henderson": "斯库特·亨德森",
    "Shaedon Sharpe": "谢登·夏普",
    "Toumani Camara": "图马尼·卡马拉",
    "Miles Norris": "迈尔斯·诺里斯",
    "Trendon Watford": "特伦登·沃特福德",
    "Justise Winslow": "贾斯蒂斯·温斯洛",
    "Caris LeVert": "卡里斯·勒韦尔",
    "Jarrett Allen": "贾勒特·阿伦",
    "Isaiah Mobley": "以赛亚·莫布利",
    "Georges Niang": "乔治·尼昂",
    "Craig Porter Jr.": "小克雷格·波特",
    "Mamadi Diakite": "马马迪·迪亚基特",
    "Trevor Keels": "特雷弗·基尔斯",
    "Charlie Brown Jr.": "小查理·布朗",
    "Moses Brown": "摩西·布朗",
    "Xavier Tillman": "泽维尔·蒂尔曼",
    "Jalen Duren": "杰伦·杜伦",
    "Isaiah Livers": "以赛亚·利弗斯",
    "Marcus Morris Sr.": "马库斯·莫里斯",
    "Monte Morris": "蒙特·莫里斯",
    "Delon Wright": "德隆·赖特",
    "Trey Alexander": "特雷·亚历山大",
    "Ryan Arcidiacono": "瑞安·阿西迪亚科诺",
    "Yuta Watanabe": "渡边雄太",
    "Facundo Campazzo": "法昆多·坎帕佐",
    "Svi Mykhailiuk": "斯维亚托斯拉夫·米哈伊柳克",
    "Theo Maledon": "泰奥·马勒东",
    "Vit Krejci": "维特·克雷伊奇",
    "Luguentz Dort": "吕冈茨·多尔特",
    "Jaylen Clark": "杰伦·克拉克",
    "Adama Sanogo": "阿达玛·萨诺戈",
    "Markquis Nowell": "马克奎斯·诺韦尔",
    "Nate Darling": "内特·达林",
    "Javonte Green": "贾冯特·格林",
    "Troy Brown Jr.": "小特洛伊·布朗",
    "Cody Martin": "科迪·马丁",
    "James Bouknight": "詹姆斯·布克奈特",
    "JT Thor": "JT·索尔",
    "Kai Jones": "凯·琼斯",
    "Davion Mintz": "达维恩·明茨",
    "Blake Wesley": "布莱克·韦斯利",
    "Christian Koloko": "克里斯蒂安·科洛克",
    "Wendell Moore Jr.": "小温德尔·摩尔",
    "MarJon Beauchamp": "马乔恩·博尚",
    "Andre Drummond": "安德烈·德拉蒙德",
    "Richaun Holmes": "里乔恩·霍姆斯",
    "Chimezie Metu": "奇梅齐耶·梅图",
    "Derrick Rose": "德里克·罗斯",
    "Thaddeus Young": "萨迪厄斯·杨",
    "George Hill": "乔治·希尔",
    "Joe Ingles": "乔·英格尔斯",
    "Danilo Gallinari": "达尼洛·加里纳利",
    "Serge Ibaka": "赛尔吉·伊巴卡",
    "Marc Gasol": "马克·加索尔",
    "Pau Gasol": "保罗·加索尔",
    "Manu Ginobili": "马努·吉诺比利",
    "Tony Parker": "托尼·帕克",
    "Tim Duncan": "蒂姆·邓肯",
    "Dirk Nowitzki": "德克·诺维茨基",
    "Kobe Bryant": "科比·布莱恩特",
    "Allen Iverson": "阿伦·艾弗森",
    "Shaquille O'Neal": "沙奎尔·奥尼尔",
    "Magic Johnson": "魔术师约翰逊",
    "Larry Bird": "拉里·伯德",
    "A.J. Green": "AJ·格林",
    "Aaron Nesmith": "阿龙·内史密斯",
    "Amari Bailey": "阿马里·贝利",
    "Anthony Black": "安东尼·布莱克",
    "Armoni Brooks": "阿蒙尼·布鲁克斯",
    "Bennedict Mathurin": "本尼迪克特·马瑟林",
    "Brandon Boston Jr.": "小布兰登·波士顿",
    "Brandon Clarke": "布兰登·克拉克",
    "Brett Maher": "布雷特·马厄",
    "Cam Thomas": "卡姆·托马斯",
    "Chris Duarte": "克里斯·杜阿尔特",
    "Cole Anthony": "科尔·安东尼",
    "Devonte' Graham": "德冯特·格雷厄姆",
    "Doug McDermott": "道格·麦克德莫特",
    "E.J. Liddell": "EJ·利德尔",
    "Evan Fournier": "埃文·富尼耶",
    "Greg Brown III": "格雷格·布朗三世",
    "Haywood Highsmith": "海伍德·海史密斯",
    "Jakob Poeltl": "雅各布·珀尔特尔",
    "Jamal Cain": "贾马尔·凯恩",
    "Jared Rhoden": "贾里德·罗登",
    "Jaylen Brown": "杰伦·布朗",
    "Jericho Sims": "杰里乔·西姆斯",
    "Jeremy Sochan": "杰里米·索汉",
    "Jett Howard": "杰特·霍华德",
    "Johnny Davis": "约翰尼·戴维斯",
    "Jonas Valanciunas": "约纳斯·瓦兰丘纳斯",
    "Jordan Nwora": "乔丹·恩沃拉",
    "Josh Christopher": "约什·克里斯托弗",
    "Josh Minott": "约什·米诺特",
    "Khyri Thomas": "凯瑞·托马斯",
    "Kira Lewis Jr.": "小基拉·刘易斯",
    "Kobe Bufkin": "科比·布夫金",
    "Kyle Anderson": "凯尔·安德森",
    "Lamar Stevens": "拉马尔·史蒂文斯",
    "Lonnie Walker IV": "朗尼·沃克四世",
    "Luke Kennard": "卢克·肯纳德",
    "Malaki Branham": "马拉基·布兰纳姆",
    "Miles Bridges": "迈尔斯·布里奇斯",
    "Nick Richards": "尼克·理查兹",
    "RJ Barrett": "RJ·巴雷特",
    "Robert Williams III": "罗伯特·威廉斯三世",
    "Saben Lee": "塞本·李",
    "Sekou Doumbouya": "塞科·敦布亚",
    "Sterling Brown": "斯特林·布朗",
    "Steven Adams": "史蒂文·亚当斯",
    "Tim Hardaway Jr.": "小蒂姆·哈达威",
    "Tre Mann": "特雷·曼恩",
    "Tristan Thompson": "特里斯坦·汤普森",
    "Ty Jerome": "泰·杰罗姆",
    "Tyrese Haliburton": "泰瑞斯·哈利伯顿",
    "Wendell Carter Jr.": "小温德尔·卡特",
    "Zach Collins": "扎克·科林斯",
    "Ziaire Williams": "扎伊尔·威廉姆斯",
    "Adrian Griffin Jr.": "小阿德里安·格里芬",
    "Andre Iguodala": "安德烈·伊戈达拉",
    "Andrew Nembhard": "安德鲁·内姆哈德",
    "Anthony Lamb": "安东尼·兰姆",
    "Armando Bacot": "阿曼多·巴科特",
    "B.J. Boston": "BJ·波士顿",
    "Ben Simmons": "本·西蒙斯",
    "Boban Marjanovic": "博班·马扬诺维奇",
    "Bones Hyland": "邦斯·海兰德",
    "Brandon Williams": "布兰登·威廉斯",
    "Brice Sensabaugh": "布莱斯·森萨博",
    "Caleb Houstan": "凯莱布·豪斯坦",
    "Chris Boucher": "克里斯·鲍彻",
    "Cole Swider": "科尔·斯威德",
    "DaRon Holmes II": "达龙·霍姆斯二世",
    "DeAndre Jordan": "德安德烈·乔丹",
    "Deividas Sirvydis": "德维达斯·西尔维迪斯",
    "Devon Dotson": "德文·多特森",
    "Dexter Dennis": "德克斯特·丹尼斯",
    "D'Marco Dunn": "德马科·邓恩",
    "Drew Peterson": "德鲁·彼得森",
    "Duane Washington Jr.": "小杜安·华盛顿",
    "Emoni Bates": "埃莫尼·贝茨",
    "Furkan Korkmaz": "富尔坎·科尔克马兹",
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
    "Mark Armstrong": "马克·阿姆斯特朗",
    "Markieff Morris": "马基夫·莫里斯",
    "Marques Bolden": "马奎斯·博尔登",
    "Matt Hurt": "马特·赫特",
    "Maxwell Lewis": "麦克斯韦尔·刘易斯",
    "Micheal Eric": "迈克尔·埃里克",
    "Miles McBride": "迈尔斯·麦克布莱德",
    "Nate Hinton": "内特·欣顿",
    "Nate Laszewski": "内特·拉斯泽夫斯基",
    "Naz Mitrou-Long": "纳兹·米特鲁-朗",
    "Nerlens Noel": "奈伦斯·诺埃尔",
    "Ochai Agbaji": "奥柴·阿巴基",
    "Oliver-Maxence Prosper": "奥利弗-马克桑斯·普罗斯珀",
    "Omari Moore": "奥马里·摩尔",
    "Pete Nance": "皮特·南斯",
    "Quincy Olivari": "昆西·奥利瓦里",
    "RayJ Dennis": "雷杰·丹尼斯",
    "Riley Minix": "莱利·米尼克斯",
    "RJ Davis": "RJ·戴维斯",
    "Rob Dillingham": "罗布·迪林厄姆",
    "Ryan Kalkbrenner": "瑞安·卡尔克布伦纳",
    "Sam Merrill": "萨姆·梅里尔",
    "Sandro Mamukelashvili": "桑德罗·马穆凯拉什维利",
    "Scotty Pippen Jr.": "小斯科蒂·皮蓬",
    "Shaq Buchanan": "沙克·布坎南",
    "Sidney Cooks": "西德尼·库克斯",
    "Skylar Mays": "斯凯拉·梅斯",
    "Tariq Castro-Fields": "塔里克·卡斯特罗-菲尔兹",
    "Taz Sherman": "塔兹·谢尔曼",
    "Terquavion Smith": "特夸维恩·史密斯",
    "Tomer Ginat": "托默·吉纳特",
    "Tre Mitchell": "特雷·米切尔",
    "Tyler Bey": "泰勒·贝",
    "Tyler Kolek": "泰勒·科莱克",
    "Tyson Etienne": "泰森·埃蒂安",
    "Umoja Gibson": "乌莫贾·吉布森",
    "Vasilije Micic": "瓦西里耶·米契奇",
    "Vernon Carey Jr.": "小弗农·凯里",
    "Victor Oladipo": "维克托·奥拉迪波",
    "Will Richardson": "威尔·理查德森",
    "Xavier Sneed": "泽维尔·斯尼德",
    "Yves Missi": "伊夫·米西",
    "Zaccharie Risacher": "扎卡里·里萨谢",
    "Zach Edey": "扎克·埃迪",
    "Zavier Simpson": "扎维尔·辛普森",
    "Thadde Vishus Young": "萨迪厄斯·杨",
    "Donovan Clingan": "多诺万·克林根",
    "Reed Sheppard": "里德·谢泼德",
    "Matas Buzelis": "马塔斯·布泽利斯",
    "Cody Williams": "科迪·威廉姆斯",
    "Jalen Williams (OKC)": "杰伦·威廉姆斯 (雷霆)",
    "Vince Williams Jr.": "小文斯·威廉姆斯",
    "GG Jackson": "GG·杰克逊",
    "Duncan Robinson": "邓肯·罗宾逊",
    "Nic Claxton": "尼古拉斯·克拉克斯顿",
    "Mikal Bridges": "米卡尔·布里奇斯",
    "Cam Johnson": "卡梅隆·约翰逊",
    "Moritz Wagner": "莫里茨·瓦格纳",
    "Dennis Schroder": "丹尼斯·施罗德",
    "Spencer Dinwiddie": "斯潘塞·丁威迪",
    "Day'Ron Sharpe": "戴龙·夏普",
    "Dorian Finney-Smith": "多里安·芬尼-史密斯",
    "Seth Curry": "塞思·库里",
    "Ben Sheppard": "本·谢泼德",
    "Obi Toppin": "奥比·托平",
    "T.J. McConnell": "T.J.麦康奈尔",
    "Jalen Smith": "杰伦·史密斯",
    "Buddy Hield": "巴迪·希尔德",
    "Myles Turner": "迈尔斯·特纳",
    "James Wiseman": "詹姆斯·怀斯曼",
    "Marvin Bagley III": "马文·巴格利三世",
    "Joe Harris": "乔·哈里斯",
    "Dennis Smith Jr.": "小丹尼斯·史密斯",
    "Harry Giles III": "哈里·贾尔斯三世",
    "Matisse Thybulle": "马蒂斯·赛布尔",
    "Anfernee Simons": "安芬尼·西蒙斯",
    "Jerami Grant": "杰拉米·格兰特",
    "Deandre Ayton": "德安德烈·艾顿",
    "Kris Murray": "克里斯·穆雷",
    "Rayan Rupert": "拉扬·吕佩尔",
    "Malcolm Brogdon": "马尔科姆·布罗格登",
    "Ish Wainright": "伊什·韦恩莱特",
    "Keon Johnson": "基翁·约翰逊",
    "John Konchar": "约翰·康查尔",
    "Santi Aldama": "桑蒂·阿尔达马",
    "Jake LaRavia": "杰克·拉拉维亚",
    "David Roddy": "大卫·罗迪",
    "Jaren Jackson Jr.": "小贾伦·杰克逊",
    "Desmond Bane": "戴斯蒙德·贝恩",
    "Marcus Smart": "马库斯·斯玛特",
    "Bismack Biyombo": "俾斯麦·比永博",
    "Javonte Smart": "贾冯特·斯玛特",
    "Josh Okogie": "约什·奥科吉",
    "Dario Saric": "达里奥·沙里奇",
    "Damion Lee": "达米恩·李",
    "Keita Bates-Diop": "凯塔·贝茨-迪奥普",
    "Darius Bazley": "达里厄斯·贝兹利",
    "Nassir Little": "纳西尔·利特尔",
    "Devin Carter": "德文·卡特",
    "Nikola Topic": "尼古拉·托皮奇",
    "Kyle Filipowski": "凯尔·菲利波夫斯基",
    "Johnny Furphy": "约翰尼·弗菲",
    "Baylor Scheierman": "贝勒·谢尔曼",
    "Jared McCain": "贾里德·麦凯恩",
    "Carlton Carrington": "卡尔顿·卡林顿",
    "Jaylon Tyson": "杰伦·泰森",
    "Kyshawn George": "凯肖恩·乔治",
    "Pacome Dadiet": "帕科姆·达迪埃",
    "Melvin Ajinca": "梅尔文·阿金萨",
    "Cam Christie": "卡姆·克里斯蒂",
    "AJ Johnson": "AJ·约翰逊",
    "Harrison Ingram": "哈里森·英格拉姆",
    "Ulrich Chomche": "乌尔里希·琼什",
    "Juan Nunez": "胡安·努涅斯",
    "Bobi Klintman": "博比·克林特曼",
    "Ajay Mitchell": "阿杰·米切尔",
    "Oso Ighodaro": "奥索·伊戈达罗",
    "Pelle Larsson": "佩勒·拉尔森",
    "Cam Spencer": "卡姆·斯潘塞",
    "Antonio Reeves": "安东尼奥·里夫斯",
    "Trevon Brazile": "特雷冯·布拉齐尔",
    "Jamal Shead": "贾马尔·谢德",
    "Keshad Johnson": "克沙德·约翰逊",
    "Adem Bona": "阿代姆·博纳",
    "Isaiah Crawford": "以赛亚·克劳福德",
    "Jalen Bridges": "杰伦·布里奇斯",
    "PJ Hall": "PJ·霍尔",
    "Quinten Post": "昆滕·波斯特",
    "Zyon Pullin": "齐昂·普林",
    "Alex Toohey": "亚历克斯·图希",
    "Mantas Rubstavicius": "曼塔斯·鲁布斯塔维修斯",
    "Trentyn Flowers": "特伦廷·弗拉沃斯",
"Adou Thiero": "阿杜·蒂埃罗",
"Anthony Gill": "安东尼·吉尔",
"Asa Newell": "阿萨·纽厄尔",
"Brandon Miller": "布兰登·米勒",
"Bryce McGowens": "布莱斯·麦高恩斯",
"Bub Carrington": "布布·卡林顿",
"Caleb Love": "凯莱布·洛夫",
"Collin Gillespie": "科林·吉莱斯皮",
"Dalen Terry": "达伦·特里",
"Danny Wolf": "丹尼·沃尔夫",
"Dean Wade": "迪恩·韦德",
"Derik Queen": "德里克·奎因",
"Dominick Barlow": "多米尼克·巴洛",
"Drake Powell": "德雷克·鲍威尔",
"Duop Reath": "杜奥普·里斯",
"Dylan Cardwell": "迪伦·卡德威尔",
"Egor Demin": "叶戈尔·杰明",
"Ethan Thompson": "伊桑·汤普森",
"Garrison Mathews": "加里森·马修斯",
"Gary Harris": "加里·哈里斯",
"Grant Williams": "格兰特·威廉姆斯",
"Isaac Okoro": "艾萨克·奥科罗",
"Isaiah Jackson": "以赛亚·杰克逊",
"Jamaree Bouyea": "贾马里·布耶",
"Jamir Watkins": "贾米尔·沃特金斯",
"Jarace Walker": "贾雷斯·沃克",
"Jeremiah Fears": "杰里迈亚·费尔斯",
"Johnny Juzang": "约翰尼·朱藏",
"Julian Phillips": "朱利安·菲利普斯",
"Justin Edwards": "贾斯汀·爱德华兹",
"KJ Simpson": "KJ·辛普森",
"Karlo Matkovic": "卡洛·马特科维奇",
"Keaton Wallace": "基顿·华莱士",
"Keon Ellis": "基翁·埃利斯",
"Kevin Huerter": "凯文·许尔特",
"Kevin Porter Jr.": "小凯文·波特",
"Kevon Looney": "凯文·卢尼",
"Khaman Maluach": "卡曼·马鲁阿奇",
"Kon Knueppel": "康·克努佩尔",
"Kyle Lowry": "凯尔·洛瑞",
"Leonard Miller": "伦纳德·米勒",
"Lonzo Ball": "朗佐·鲍尔",
"Mark Williams": "马克·威廉姆斯",
"Mason Plumlee": "梅森·普拉姆利",
"Maxime Raynaud": "马克西姆·雷诺",
"Micah Peavy": "迈卡·皮维",
"Mouhamed Gueye": "穆罕默德·盖伊",
"Nae'Qwan Tomlin": "纳'奎恩·汤姆林",
"Nick Smith Jr.": "小尼克·史密斯",
"Nigel Hayes-Davis": "奈杰尔·海斯-戴维斯",
"Nique Clifford": "尼克·克利福德",
"Noah Clowney": "诺阿·克劳尼",
"Nolan Traore": "诺兰·特拉奥雷",
"Pascal Siakam": "帕斯卡尔·西亚卡姆",
"Patrick Williams": "帕特里克·威廉姆斯",
"Quenton Jackson": "昆顿·杰克逊",
"Rasheer Fleming": "拉希尔·弗莱明",
"Ryan Rollins": "瑞安·罗林斯",
"Sion James": "锡安·詹姆斯",
"Terrence Shannon Jr.": "小特伦斯·香农",
"Thomas Bryant": "托马斯·布莱恩特",
"Tidjane Salaun": "蒂贾内·萨隆",
"Tony Bradley": "托尼·布拉德利",
"Tre Johnson": "特雷·约翰逊",
"Tre Jones": "特雷·琼斯",
"Tristan Vukcevic": "特里斯坦·武切维奇",
"Tyrese Martin": "泰雷斯·马丁",
"Tyrese Proctor": "泰雷斯·普罗克特",
"VJ Edgecombe": "VJ·埃奇库姆",
"Will Riley": "威尔·赖利",
"Yang Hansen": "杨瀚森"
}


def translate_player_name(name):
    """将英文球员名转为中文，若无则返回原名"""
    if not name:
        return name
    
    name = name.strip()
    
    # 首先尝试完全匹配
    if name in player_translation:
        return player_translation[name]
    
    # 尝试处理Jr./Sr./II/III/IV等后缀
    name_parts = name.split()
    if len(name_parts) > 1:
        # 定义常见的后缀
        suffixes = ['Jr.', 'Jr', 'Sr.', 'Sr', 'II', 'III', 'IV', 'V']
        
        # 检查最后一个部分是否是后缀
        if name_parts[-1] in suffixes:
            base_name = ' '.join(name_parts[:-1])
            
            # 尝试匹配基础名称
            if base_name in player_translation:
                translated_base = player_translation[base_name]
                suffix = name_parts[-1]
                suffix_map = {
                    'Jr.': '小', 'Jr': '小',
                    'Sr.': '老', 'Sr': '老',
                    'II': '二世', 'III': '三世', 'IV': '四世', 'V': '五世'
                }
                if suffix in suffix_map:
                    return f"{translated_base}{suffix_map[suffix]}"
                return translated_base
    
    # 模糊匹配：忽略中间名缩写
    if '.' in name:
        # 将 "A.J. Green" 转换为 "AJ Green" 等
        simple_name = name.replace('.', '').replace(' ', '')
        for eng_name in player_translation:
            simple_eng = eng_name.replace('.', '').replace(' ', '')
            if simple_name.lower() == simple_eng.lower():
                return player_translation[eng_name]
    
    # 部分匹配：检查是否有相似的名字
    for eng_name, chi_name in player_translation.items():
        # 忽略大小写比较
        if eng_name.lower() in name.lower() or name.lower() in eng_name.lower():
            return chi_name
    
    # 尝试匹配不带"小"前缀的中文名
    if '小' not in name:
        for eng_name, chi_name in player_translation.items():
            if chi_name.startswith('小') and eng_name in name:
                return chi_name
    
    # 记录未翻译的名称以便调试
    if name not in ['DNP', 'N/A', '--', '']:
        st.session_state.untranslated_players.add(name)
    
    return name  # 返回原名

# ====== API 数据获取函数 ======
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
        # 尝试第一个API端点
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        resp = requests.get(url, params={'event': event_id}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('boxscore') and data.get('boxscore').get('players'):
                return data
        
        # 如果第一个失败，尝试第二个API端点
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/boxscore?event={event_id}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
            
        return None
    except Exception as e:
        return None

def format_time(t):
    """格式化时间"""
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

def safe_int(value, default=0):
    """安全地将值转换为整数"""
    if not value:
        return default
    try:
        # 处理 "5/10" 这样的投篮数据
        if '/' in str(value):
            return int(str(value).split('/')[0])
        # 处理纯数字
        return int(float(str(value)))
    except:
        return default

def parse_player_stats(game_data):
    """解析球员统计数据"""
    try:
        if not game_data or 'boxscore' not in game_data:
            return [], []
            
        players_section = game_data.get('boxscore', {}).get('players', [])
        if not players_section or len(players_section) < 2:
            return [], []

        # 尝试按索引获取主客场球员数据
        home_players = None
        away_players = None
        
        # 首先尝试通过索引获取
        if len(players_section) >= 2:
            away_players = players_section[0]
            home_players = players_section[1]
        else:
            # 如果只有一组数据，可能是不同的结构
            return [], []

        def extract_team_data(team_data):
            """提取单个球队的球员数据"""
            if not team_data:
                return []
                
            stats_list = team_data.get('statistics', [])
            if not stats_list:
                return []
                
            # 查找主要统计项（通常第一个是球员统计）
            main_stat = None
            for stat in stats_list:
                athletes = stat.get('athletes', [])
                labels = stat.get('labels', [])
                if athletes and ('PTS' in labels or '得分' in labels):
                    main_stat = stat
                    break
            
            if not main_stat:
                return []
                
            labels = main_stat.get('labels', [])
            athletes = main_stat.get('athletes', [])
            
            parsed = []
            for ath in athletes:
                try:
                    # 获取球员名
                    athlete_data = ath.get('athlete', {})
                    name_en = (athlete_data.get('displayName', '') or 
                              athlete_data.get('fullName', '') or 
                              athlete_data.get('shortName', '') or 
                              ath.get('displayName', '') or 
                              ath.get('name', ''))
                    
                    name_en = str(name_en).strip()
                    if not name_en or name_en in ['DNP', 'N/A', '--', 'null', 'None', 'DID NOT PLAY', 'NOT AVAILABLE']:
                        continue
                    
                    # 翻译球员名
                    name_cn = translate_player_name(name_en)
                    
                    raw_vals = ath.get('stats', [])
                    if not raw_vals:
                        continue
                    
                    # 创建统计映射
                    stat_map = {}
                    for i, label in enumerate(labels):
                        if i < len(raw_vals):
                            value = raw_vals[i]
                            if isinstance(value, (int, float)):
                                value = str(value)
                            elif value is None:
                                value = ''
                            else:
                                value = str(value).strip()
                            stat_map[label] = value
                    
                    # 安全地获取各项数据
                    def get_shot_value(key, default='0-0'):
                        value = stat_map.get(key, default)
                        if not value:
                            value = default
                        return str(value)
                    
                    def get_stat_value(key, default='0'):
                        value = stat_map.get(key, default)
                        if not value:
                            value = default
                        return str(value)
                    
                    # 解析投篮数据
                    fg_str = get_shot_value('FG', '0-0').replace('/', '-')
                    three_str = get_shot_value('3PT', '0-0').replace('/', '-')
                    ft_str = get_shot_value('FT', '0-0').replace('/', '-')
                    
                    # 分割投篮数据
                    fg_parts = fg_str.split('-') if '-' in fg_str else ('0', '0')
                    three_parts = three_str.split('-') if '-' in three_str else ('0', '0')
                    ft_parts = ft_str.split('-') if '-' in ft_str else ('0', '0')
                    
                    fgm = fg_parts[0] if len(fg_parts) >= 1 else '0'
                    fga = fg_parts[1] if len(fg_parts) >= 2 else '0'
                    threepm = three_parts[0] if len(three_parts) >= 1 else '0'
                    threepa = three_parts[1] if len(three_parts) >= 2 else '0'
                    ftm = ft_parts[0] if len(ft_parts) >= 1 else '0'
                    fta = ft_parts[1] if len(ft_parts) >= 2 else '0'
                    
                    # 确保数字有效性
                    def safe_num(val):
                        try:
                            num = float(val)
                            return str(int(num)) if num.is_integer() else str(round(num, 1))
                        except:
                            return '0'
                    
                    # 获取其他统计
                    minutes = format_time(stat_map.get('MIN', '0'))
                    pts = safe_num(get_stat_value('PTS', '0'))
                    reb = safe_num(get_stat_value('REB', '0'))
                    ast = safe_num(get_stat_value('AST', '0'))
                    tov = safe_num(get_stat_value('TO', '0'))
                    
                    # 创建球员数据字典
                    player_data = {
                        '球员': name_cn,
                        '时间': minutes,
                        '得分': pts,
                        '投篮': f"{fgm}/{fga}",
                        '三分': f"{threepm}/{threepa}",
                        '罚球': f"{ftm}/{fta}",
                        '篮板': reb,
                        '助攻': ast,
                        '失误': tov
                    }
                    
                    # 只添加有数据的球员（至少得分、篮板、助攻或时间不为0）
                    has_data = False
                    if (safe_int(pts) > 0 or safe_int(reb) > 0 or safe_int(ast) > 0 or 
                        safe_int(fgm) > 0 or safe_int(threepm) > 0 or safe_int(ftm) > 0):
                        has_data = True
                    
                    # 检查上场时间是否大于0
                    if minutes != '0:00' and minutes != '0':
                        has_data = True
                    
                    if has_data:
                        parsed.append(player_data)
                        
                except Exception as e:
                    # 跳过单个球员的错误
                    continue
            
            return parsed

        away_data = extract_team_data(away_players)
        home_data = extract_team_data(home_players)

        return away_data, home_data

    except Exception as e:
        return [], []

# ====== Streamlit 界面 ======
# Sidebar
with st.sidebar:
    st.header("⚙️ 查询设置")
    selected_date = st.date_input(
        "选择日期",
        value=now_beijing.date(),
        min_value=now_beijing.date() - timedelta(days=3),
        max_value=now_beijing.date() + timedelta(days=3)
    )
    
    if st.button("🧹 清除缓存"):
        st.cache_data.clear()
        st.success("缓存已清除")

# Main
st.subheader(f"📅 {selected_date.strftime('%Y-%m-%d')} 赛程")

with st.spinner("加载赛程..."):
    schedule = fetch_nba_schedule(selected_date.strftime('%Y-%m-%d'))

if not schedule or 'events' not in schedule:
    st.error("无法获取数据，请稍后重试")
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

    # 显示比赛信息
    cols = st.columns([2, 1, 0.5, 1, 2])
    cols[0].markdown(f"**{away_name}**")
    cols[1].markdown(f"**{away_score}**")
    cols[2].markdown("**VS**")
    cols[3].markdown(f"**{home_score}**")
    cols[4].markdown(f"**{home_name}**")
    st.caption(f"{badge} | {desc} | ⏰ {bj_time}")

    # 如果比赛进行中或已结束，显示球员数据
    if state in ['in', 'post']:
        with st.spinner(f"加载{away_name} vs {home_name}的球员数据..."):
            game_data = fetch_player_stats(event['id'])
            if game_data:
                away_p, home_p = parse_player_stats(game_data)
                
                # 只显示有数据的比赛
                if away_p or home_p:
                    st.subheader("📊 球员数据")
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown(f"**{away_name}**")
                        if away_p:
                            df = pd.DataFrame(away_p)
                            if not df.empty:
                                # 按得分排序
                                df['得分'] = pd.to_numeric(df['得分'], errors='coerce')
                                df = df.sort_values('得分', ascending=False)
                                df['得分'] = df['得分'].astype(str)
                                st.dataframe(df, hide_index=True, use_container_width=True)
                            else:
                                st.info("暂无球员数据")
                        else:
                            st.info("暂无球员数据")
                    
                    with c2:
                        st.markdown(f"**{home_name}**")
                        if home_p:
                            df = pd.DataFrame(home_p)
                            if not df.empty:
                                # 按得分排序
                                df['得分'] = pd.to_numeric(df['得分'], errors='coerce')
                                df = df.sort_values('得分', ascending=False)
                                df['得分'] = df['得分'].astype(str)
                                st.dataframe(df, hide_index=True, use_container_width=True)
                            else:
                                st.info("暂无球员数据")
                        else:
                            st.info("暂无球员数据")
                else:
                    # 只有比赛状态为进行中或已结束但没有数据时才显示提示
                    st.info("球员数据暂未更新，请稍后刷新")
            else:
                st.warning("球员数据加载失败，请稍后重试")

    if i < len(events) - 1:
        st.divider()

st.divider()
col1, col2, col3 = st.columns([3, 1, 1])
col1.caption(f"更新于: {datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')}")

if col2.button("🔄 刷新数据"):
    st.cache_data.clear()
    st.rerun()

# 显示未翻译的球员名
if st.session_state.untranslated_players:
    with st.expander("⚠️ 未翻译球员名（需要添加到映射表）"):
        st.write("以下球员名未找到翻译，请添加到 `player_translation` 字典中：")
        for player in sorted(st.session_state.untranslated_players):
            st.text(f'"{player}": "",')
