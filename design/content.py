"""30 din x 3 products = 90 nayi posts. Chalao: python design/content.py  -> posts.json"""
import json
import re
from pathlib import Path

H = "<span class='hl'>"
E = "</span>"

SB = [
    # ---- cycle 1
    dict(type="hero", v=0, tag="Immunity", kicker="Himalaya નું Superfruit", title=f"રોજની {H}Immunity{E}<br>એક Capsule માં!",
         sub="Vitamin A, B, C, E, K + Omega 3, 6, 7, 9",
         items=[["shield", "Immunity Support"], ["sparkle", "Natural Skin Glow"], ["hair", "Hair Strength"], ["bolt", "Daily Energy"]],
         badges=["Veg Capsules", "1000 mg"]),
    dict(type="fact", v=2, title=f"Sea Buckthorn ને {H}Himalaya નું Superfruit{E} કહેવાય છે",
         body="આ નાની નારંગી બેરી લદ્દાખ અને હિમાલયના ઠંડા વિસ્તારોમાં ઉગે છે — કુદરતી પોષણથી ભરપૂર."),
    dict(type="checklist", v=0, kicker="આજકાલ…", title=f"શું તમને પણ<br>{H}આવું લાગે છે?{E}",
         items=["ત્વચા નિસ્તેજ લાગે", "વાળ નબળા લાગે", "જલ્દી થાક લાગે", "વારંવાર શરદી-ખાંસી"], sub="તો રોજના પોષણ પર ધ્યાન આપો."),
    dict(type="tip", v=1, icon="water", title=f"દિવસમાં {H}8-10 ગ્લાસ{E}<br>પાણી પીઓ",
         body="Skin glow અને સારા પાચન માટે hydration સૌથી સરળ રસ્તો છે.", pair="Glow from within"),
    dict(type="spotlight", v=2, kicker="Nutrient Spotlight", title=f"દુર્લભ {H}Omega-7{E}", big="Ω-7", big_sub="Omega-7",
         body="Sea Buckthorn એ Omega-7 ના થોડા કુદરતી સ્ત્રોતોમાંનું એક છે — ત્વચા માટે ખાસ."),
    dict(type="faq", v=0, title="Sea Buckthorn Capsule કોણ લઈ શકે?",
         body="Immunity, skin અને hair માટે રોજનું પોષણ ઈચ્છતા પુખ્ત વયના લોકો. ગર્ભાવસ્થા કે દવા ચાલુ હોય તો ડૉક્ટરની સલાહ લો."),
    dict(type="quote", v=2, title=f"સ્વાસ્થ્ય એ જ<br>{H}સાચી સંપત્તિ{E}", body="Health is the real wealth — આજથી જ પોતાની કાળજી લો.", pair="Daily wellness partner"),
    dict(type="myth", v=0, title="Vitamin C માટે<br>ફક્ત સંતરા જ?", myth="Vitamin C ફક્ત સંતરા અને લીંબુમાંથી જ મળે.",
         fact="Sea Buckthorn બેરીમાં Vitamin C ભરપૂર હોય છે — સાથે Omega અને Antioxidants પણ."),
    dict(type="steps", v=0, kicker="રોજની Healthy Routine", title=f"Glow & Immunity<br>માટે {H}3 આદત{E}",
         steps=["સવારે હુંફાળું પાણી", "દિવસમાં 30 મિનિટ ચાલવું", "Sea Buckthorn — રોજનું પોષણ"]),
    dict(type="cta", v=1, kicker="5 Vitamins + 4 Omegas", title=f"એક Capsule,<br>{H}અનેક ફાયદા{E}",
         items=["Vitamin A, B, C", "Vitamin E, K", "Omega 3,6,7,9", "Antioxidants", "Veg Capsules", "1000 mg"]),
    # ---- cycle 2
    dict(type="hero", v=1, tag="Skin Glow", kicker="અંદરથી Glow", title=f"ચમકતી {H}ત્વચા{E}<br>અંદરના પોષણથી",
         sub="Omega-7 + Vitamin C + Vitamin E",
         items=[["sparkle", "Natural Glow"], ["drop", "Skin Hydration"], ["heart", "Antioxidant Power"], ["sun", "Fresh Look"]],
         badges=["Nutraceutical", "Veg Capsules"]),
    dict(type="fact", v=0, title=f"Sea Buckthorn માં {H}Omega 3, 6, 7, 9{E} — ચારેય!",
         body="મોટાભાગના ખોરાકમાં એક-બે Omega મળે, પણ Sea Buckthorn માં ચારેય કુદરતી રીતે હોય છે."),
    dict(type="checklist", v=2, kicker="Hair Care", title=f"વાળ માટે<br>{H}આ ભૂલો?{E}",
         items=["ખૂબ ગરમ પાણીથી વાળ ધોવા", "ઓછું પાણી પીવું", "અપૂરતી ઊંઘ", "પોષણ વગરનો ખોરાક"], sub="વાળને અંદરથી પણ પોષણ આપો."),
    dict(type="tip", v=0, icon="moon", title=f"રોજ {H}7-8 કલાકની{E}<br>ઊંઘ લો",
         body="ઊંઘ દરમિયાન શરીર પોતાને repair કરે છે — ત્વચા અને immunity બંને માટે જરૂરી.", pair="Beauty sleep + પોષણ"),
    dict(type="spotlight", v=0, kicker="Nutrient Spotlight", title=f"{H}Vitamin C{E} નો ખજાનો", big="C", big_sub="Vitamin C", big_size=150,
         body="Vitamin C રોગપ્રતિકારક શક્તિ અને collagen બનાવવામાં મદદરૂપ છે."),
    dict(type="faq", v=2, title="Sea Buckthorn Capsule ક્યારે લેવી?",
         body="Label પર આપેલી રીત મુજબ, સામાન્ય રીતે ભોજન પછી. વધુ માહિતી માટે અમને Call કે WhatsApp કરો."),
    dict(type="quote", v=1, title=f"Glow એ આદત છે,<br>{H}Filter નહીં{E}", body="રોજનું પોષણ, પાણી અને ઊંઘ — આ જ સાચો beauty secret.", pair="Glow naturally"),
    dict(type="myth", v=2, title="Skin Care એટલે<br>ફક્ત Cream?", myth="સારી ત્વચા માટે બહારથી cream લગાવવી પૂરતી છે.",
         fact="ત્વચાને અંદરથી પણ પોષણ જોઈએ — Vitamins, Omega અને પૂરતું પાણી."),
    dict(type="steps", v=2, kicker="Immunity Routine", title=f"બદલાતી મોસમમાં<br>{H}તૈયારી{E}",
         steps=["હળદરવાળું દૂધ કે ઉકાળો", "મોસમી ફળો ખાઓ", "રોજનું પોષણ — Sea Buckthorn"]),
    dict(type="cta", v=0, kicker="Daily Wellness Partner", title=f"Immunity + Glow<br>{H}એક સાથે!{E}",
         items=["Immunity", "Skin Glow", "Hair Strength", "Energy", "Heart Health", "Digestion"]),
    # ---- cycle 3
    dict(type="hero", v=2, tag="Energy", kicker="થાક દૂર, તાજગી ભરપૂર", title=f"દિવસભર {H}Active{E}<br>રહો!",
         sub="Vitamins + Antioxidants નો કુદરતી સાથ",
         items=[["bolt", "Daily Energy"], ["shield", "Strong Immunity"], ["heart", "Heart Health"], ["leaf", "Natural Source"]],
         badges=["1000 mg", "Nutraceutical"]),
    dict(type="fact", v=1, title=f"Sea Buckthorn નો ઉપયોગ {H}સદીઓથી{E} થાય છે",
         body="હિમાલય અને તિબેટની પરંપરાગત ચિકિત્સામાં Sea Buckthorn વર્ષોથી વપરાતી આવી છે."),
    dict(type="checklist", v=0, kicker="Immunity Check", title=f"વારંવાર બીમાર<br>{H}પડો છો?{E}",
         items=["મોસમ બદલાય ને શરદી", "જલ્દી થાક લાગે", "ઓછી ભૂખ", "ઊંઘ પૂરી ન થાય"], sub="તો immunity ને આપો રોજનો સાથ."),
    dict(type="tip", v=2, icon="walk", title=f"જમ્યા પછી<br>{H}10 મિનિટ{E} ચાલો",
         body="પાચન સુધરે, શરીર હળવું લાગે અને ઊંઘ પણ સારી આવે.", pair="Small habit, big change"),
    dict(type="spotlight", v=1, kicker="Nutrient Spotlight", title=f"{H}Vitamin E{E} — Skin નો મિત્ર", big="E", big_sub="Vitamin E", big_size=150,
         body="Vitamin E એક શક્તિશાળી antioxidant છે, જે ત્વચાના રક્ષણમાં મદદરૂપ છે."),
    dict(type="faq", v=0, title="શું આ દવા છે?",
         body="ના. Niroza Sea Buckthorn એક Nutraceutical (પોષણ પૂરક) છે — રોજના પોષણ માટે. સારવાર માટે ડૉક્ટરની સલાહ લો."),
    dict(type="quote", v=0, title=f"નાની આદતો,<br>{H}મોટા ફેરફાર{E}", body="રોજ એક Healthy પસંદગી — ફરક તમે જાતે જોશો.", pair="Start today"),
    dict(type="myth", v=1, title="Supplements ફક્ત<br>વડીલો માટે?", myth="Vitamins અને supplements ફક્ત મોટી ઉંમરના લોકો માટે છે.",
         fact="આજની દોડધામવાળી જીવનશૈલીમાં યુવાનોને પણ પોષણની ખોટ પડી શકે છે."),
    dict(type="steps", v=0, kicker="Healthy Skin Routine", title=f"Glow માટે<br>{H}3 Steps{E}",
         steps=["સવારે 2 ગ્લાસ પાણી", "ખોરાકમાં ફળ-શાકભાજી", "Sea Buckthorn — રોજનું પોષણ"]),
    dict(type="cta", v=2, kicker="Niroza નું વચન", title=f"શુદ્ધ. કુદરતી.<br>{H}વિશ્વસનીય.{E}",
         items=["Veg Capsules", "1000 mg", "Vitamin A to K", "Omega 3 to 9", "Antioxidants", "Nutraceutical"]),
]

B12 = [
    dict(type="hero", v=0, tag="Energy", kicker="Plant-Based Power", title=f"થાક ને કહો<br>{H}Bye-Bye!{E}",
         sub="Moringa • Amla • Barley Grass",
         items=[["bolt", "Full Day Energy"], ["brain", "Nerve Support"], ["drop", "Healthy Blood"], ["leaf", "100% Plant-Based"]],
         badges=["Veg Capsules", "Vegan"]),
    dict(type="fact", v=2, title=f"શાકાહારી લોકોમાં {H}B12 ની ઉણપ{E} ખૂબ સામાન્ય છે",
         body="B12 મુખ્યત્વે દૂધ, ઈંડા અને માંસમાંથી મળે છે. એટલે vegetarian diet માં ઘણી વાર ઓછું પડે છે."),
    dict(type="checklist", v=0, kicker="B12 ની ઉણપના સંકેત", title=f"શું તમને પણ<br>{H}આવું થાય છે?{E}",
         items=["સતત થાક અને નબળાઈ", "હાથ-પગમાં ઝણઝણાટી", "ભૂલી જવાની ટેવ", "મૂડ ઓછો રહે"], sub="તો B12 ની તપાસ જરૂર કરાવો."),
    dict(type="tip", v=1, icon="sun", title=f"સવારે {H}15 મિનિટ{E}<br>તડકામાં બેસો",
         body="Vitamin D મળે, મૂડ સારો રહે અને દિવસની શરૂઆત energy સાથે થાય.", pair="Daily energy partner"),
    dict(type="spotlight", v=2, kicker="Nutrient Spotlight", title=f"{H}Vitamin B12{E} શા માટે જરૂરી?", big="B12", big_sub="Cobalamin",
         body="B12 energy બનાવવા, nerves ને સ્વસ્થ રાખવા અને red blood cells બનાવવામાં મદદ કરે છે."),
    dict(type="faq", v=0, title="B12 કેપ્સ્યુલ કોણ લઈ શકે?",
         body="જેમને થાક-નબળાઈ લાગે, જે શાકાહારી છે અથવા દોડધામવાળું જીવન જીવે છે. બીમારી કે દવા ચાલુ હોય તો ડૉક્ટરની સલાહ લો."),
    dict(type="quote", v=2, title=f"Energy એ જ<br>{H}Productivity{E}", body="સારું પોષણ = વધુ સારો દિવસ.", pair="Start your day with strength"),
    dict(type="myth", v=0, title="B12 ની ઉણપ<br>ફક્ત વડીલોમાં?", myth="B12 ની ઉણપ ફક્ત મોટી ઉંમરના લોકોને જ થાય.",
         fact="શાકાહારી યુવાનો અને સ્ત્રીઓમાં પણ B12 ની ઉણપ ખૂબ સામાન્ય છે."),
    dict(type="steps", v=0, kicker="Energy Routine", title=f"દિવસભર Fresh<br>રહેવાની {H}3 ટિપ્સ{E}",
         steps=["સવારનો નાસ્તો છોડશો નહીં", "દર 2 કલાકે પાણી પીઓ", "Niroza B12 — રોજનો સાથ"]),
    dict(type="cta", v=1, kicker="થાકને કહો Bye-Bye", title=f"Full Day {H}Energy{E}",
         items=["100% Plant-Based", "Vegan Friendly", "Veg Capsules", "Moringa", "Amla", "Barley Grass"]),
    # ---- cycle 2
    dict(type="hero", v=2, tag="Focus", kicker="મગજ માટે પોષણ", title=f"Focus અને<br>{H}Freshness{E}",
         sub="Nerves ને આપો B12 નો સાથ",
         items=[["brain", "Focus Support"], ["heart", "Calm Mind"], ["bolt", "Mental Energy"], ["leaf", "Vegan Friendly"]],
         badges=["Plant-Based", "Veg Capsules"]),
    dict(type="fact", v=0, title=f"B12 ની ઉણપ ધીમે ધીમે {H}વર્ષો{E} પછી દેખાય",
         body="શરીર B12 નો સંગ્રહ કરે છે, એટલે ઉણપના લક્ષણો મોડા દેખાય. નિયમિત તપાસ કરાવવી સારી."),
    dict(type="checklist", v=2, kicker="Office / Study Life", title=f"કામમાં<br>{H}મન નથી લાગતું?{E}",
         items=["બપોર પછી ઊંઘ આવે", "Focus ટકતું નથી", "વાતે વાતે ચીડ", "સવારે ઊઠવાનું મન ન થાય"], sub="પોષણ, ઊંઘ અને પાણી — ત્રણેય પર ધ્યાન આપો."),
    dict(type="tip", v=0, icon="water", title=f"ચા-કોફી ઓછી,<br>{H}પાણી વધુ{E}",
         body="વધુ caffeine થી ઊંઘ બગડે છે. દિવસ દરમિયાન પાણી અને છાશ પીઓ.", pair="Stay fresh naturally"),
    dict(type="spotlight", v=0, kicker="Ingredient Spotlight", title=f"{H}Moringa{E} ની તાકાત", big="Moringa", big_size=76, big_sub="સરગવો",
         body="સરગવાના પાન (Moringa) કુદરતી પોષણનો ભંડાર છે — Niroza B12 માં ખાસ સામેલ."),
    dict(type="faq", v=2, title="Plant-Based B12 એટલે શું?",
         body="Vegetarian અને vegan લોકો માટે યોગ્ય — Moringa, Amla, Barley Grass જેવા વનસ્પતિ આધારિત ઘટકો સાથે."),
    dict(type="quote", v=1, title=f"શરીર સાથ આપે,<br>તો જ {H}સપના{E} પૂરા થાય", body="પોતાના સ્વાસ્થ્યને પ્રાથમિકતા આપો.", pair="Power your dreams"),
    dict(type="myth", v=2, title="થાક એટલે<br>ફક્ત ઊંઘની કમી?", myth="થાક લાગે તો ફક્ત વધુ ઊંઘ લેવી પૂરતી છે.",
         fact="સતત થાક પોષણની ઉણપ (જેમ કે B12 કે Iron) નો સંકેત પણ હોઈ શકે છે."),
    dict(type="steps", v=2, kicker="Vegetarian છો? તો આ વાંચો", title=f"B12 માટે<br>{H}3 સરળ ઉપાય{E}",
         steps=["દૂધ, દહીં, છાશ રોજ લો", "વર્ષમાં એક વાર B12 test", "જરૂર મુજબ supplement"]),
    dict(type="cta", v=0, kicker="Start Your Day With Strength", title=f"રોજની {H}Energy{E},<br>રોજનો સાથ",
         items=["Moringa", "Amla", "Barley Grass", "Veg Capsules", "Plant-Based", "Vegan Friendly"]),
    # ---- cycle 3
    dict(type="hero", v=1, tag="Nerves", kicker="ઝણઝણાટી? સુન્નપણું?", title=f"Nerves ને આપો<br>{H}પોષણ{E}",
         sub="B12 — Nervous System માટે જરૂરી",
         items=[["brain", "Nerve Health"], ["bolt", "Less Tiredness"], ["drop", "Blood Formation"], ["leaf", "Plant-Based"]],
         badges=["60 Veg Capsules", "Vegan"]),
    dict(type="fact", v=1, title=f"આમળામાં કુદરતી {H}Vitamin C{E} ભરપૂર છે",
         body="આયુર્વેદમાં આમળાને રસાયન ગણવામાં આવે છે — Niroza B12 માં Amla પણ સામેલ છે."),
    dict(type="checklist", v=0, kicker="Women's Wellness", title=f"મહિલાઓ,<br>{H}ધ્યાન આપો!{E}",
         items=["ઘરકામમાં જલ્દી થાક", "ચક્કર જેવું લાગે", "વાળ ખરવા", "ચહેરો ફિક્કો લાગે"], sub="પોતાની કાળજી પણ એટલી જ જરૂરી છે."),
    dict(type="tip", v=2, icon="clock", title=f"રોજ એક જ સમયે<br>{H}સૂવો-ઊઠો{E}",
         body="નિયમિત ઊંઘનું ટાઇમટેબલ energy અને મૂડ બંને સુધારે છે.", pair="Routine = Energy"),
    dict(type="spotlight", v=1, kicker="Ingredient Spotlight", title=f"{H}Barley Grass{E} — લીલું પોષણ", big="Barley", big_size=84, big_sub="જવના જવારા",
         body="જવના જવારા (Barley Grass) chlorophyll અને antioxidants થી ભરપૂર છે."),
    dict(type="faq", v=0, title="B12 કેપ્સ્યુલ ક્યારે લેવી?",
         body="Label પર આપેલી રીત મુજબ, સામાન્ય રીતે ભોજન પછી પાણી સાથે. વધુ માહિતી માટે Call / WhatsApp કરો."),
    dict(type="quote", v=0, title=f"Healthy Body,<br>{H}Happy Mind{E}", body="શરીર અને મન — બંનેનું પોષણ જરૂરી.", pair="Clean. Vegan. Ayurvedic."),
    dict(type="myth", v=1, title="શાકાહારીને<br>B12 ની જરૂર નથી?", myth="શાકાહારી ખોરાકમાંથી બધું જ પોષણ મળી જાય છે.",
         fact="વનસ્પતિ ખોરાકમાં B12 બહુ ઓછું હોય છે — એટલે શાકાહારીઓએ ખાસ ધ્યાન રાખવું."),
    dict(type="steps", v=0, kicker="Morning Energy Ritual", title=f"સવારની<br>{H}Power Routine{E}",
         steps=["ઊઠીને 1 ગ્લાસ હુંફાળું પાણી", "10 મિનિટ યોગ / Stretching", "પૌષ્ટિક નાસ્તો + Niroza B12"]),
    dict(type="cta", v=2, kicker="Clean. Vegan. Ayurvedic.", title=f"Niroza<br>{H}Vitamin B12{E}",
         items=["100% Plant-Based", "Vegan Friendly", "Moringa", "Amla", "Energy", "Nerve Support"]),
]

DG = [
    dict(type="hero", v=0, tag="Digestion", kicker="આયુર્વેદ આધારિત", title=f"પાચન માટે<br>{H}ખાસ સાથી{E}",
         sub="વરિયાળી Flavour • Plant-Based",
         items=[["stomach", "પેટ ફૂલવામાં રાહત"], ["flame", "Acidity માં રાહત"], ["leaf", "ભૂખ વધારે"], ["heart", "હળવું પેટ"]],
         badges=["100g Pack", "FSSAI મંજૂર"]),
    dict(type="fact", v=2, title=f"આયુર્વેદમાં સારું પાચન એટલે મજબૂત {H}'અગ્નિ'{E}",
         body="પાચન-અગ્નિ સારો હોય તો શરીર ખોરાકમાંથી પૂરું પોષણ લઈ શકે છે."),
    dict(type="checklist", v=0, kicker="જમ્યા પછી…", title=f"આમાંથી કંઈ<br>{H}થાય છે?{E}",
         items=["પેટ ફૂલી જાય છે", "ગેસ અને ભારેપણું", "ખાટા ઓડકાર", "ભૂખ ઓછી લાગે"], sub="તો પાચનને આપો કુદરતી સાથ."),
    dict(type="tip", v=1, icon="clock", title=f"જમ્યા પછી<br>{H}તરત ન સૂવો{E}",
         body="ભોજન અને ઊંઘ વચ્ચે 2-3 કલાકનો gap રાખવાથી acidity ઓછી થાય છે.", pair="પાચન માટે ખાસ"),
    dict(type="spotlight", v=2, kicker="રસોડાનો ખજાનો", title=f"{H}વરિયાળી{E} — પાચનની મિત્ર", big="Fennel", big_size=84, big_sub="વરિયાળી",
         body="જમ્યા પછી વરિયાળી ખાવાની આપણી પરંપરા છે — કારણ કે તે પાચનમાં મદદરૂપ ગણાય છે."),
    dict(type="faq", v=0, title="Digest Powder કેવી રીતે લેવો?",
         body="1 ચમચી, ભોજન પછી, હુંફાળા પાણી સાથે — દિવસમાં 2 વાર."),
    dict(type="quote", v=2, title=f"સારું પાચન એટલે<br>{H}સારું આરોગ્ય{E}", body="આયુર્વેદ કહે છે — સ્વાસ્થ્યની શરૂઆત પેટથી થાય છે.", pair="પાચન માટે ખાસ"),
    dict(type="myth", v=0, title="Acidity ફક્ત<br>તીખું ખાવાથી?", myth="Acidity ફક્ત તીખો-તળેલો ખોરાક ખાવાથી જ થાય.",
         fact="મોડું જમવું, ઓછી ઊંઘ, તણાવ અને અનિયમિત ભોજન પણ acidity વધારી શકે છે."),
    dict(type="steps", v=0, kicker="ઉપયોગની સરળ રીત", title=f"3 Steps માં<br>{H}હળવું પેટ{E}",
         steps=["1 ચમચી Digest Powder લો", "હુંફાળા પાણી સાથે લો", "દિવસમાં 2 વાર, ભોજન પછી"]),
    dict(type="cta", v=1, kicker="જમ્યા પછી ભારેપણું?", title=f"હવે {H}હળવું પેટ{E}",
         items=["Gas માં રાહત", "Acidity માં રાહત", "Bloating ઓછું", "ભૂખ વધારે", "Plant-Based", "100g Pack"]),
    # ---- cycle 2
    dict(type="hero", v=2, tag="Gut Health", kicker="Healthy Gut, Happy Life", title=f"પેટ સારું,<br>{H}મૂડ સારો!{E}",
         sub="રોજનું પાચન રાખો નિયમિત",
         items=[["stomach", "Regular Digestion"], ["flame", "ઓછી Acidity"], ["leaf", "Natural Ingredients"], ["sun", "Fresh Feeling"]],
         badges=["વરિયાળી Flavour", "100g"]),
    dict(type="fact", v=0, title=f"આપણી {H}Immunity{E} નો મોટો ભાગ પેટ સાથે જોડાયેલો છે",
         body="સ્વસ્થ આંતરડાં (gut) શરીરની રોગપ્રતિકારક શક્તિ માટે પણ ખૂબ મહત્વના છે."),
    dict(type="checklist", v=2, kicker="આ આદતો પાચન બગાડે", title=f"શું તમે પણ<br>{H}આવું કરો છો?{E}",
         items=["ઉતાવળે જમવું", "મોડી રાત્રે જમવું", "જમતી વખતે Mobile", "ઓછું પાણી પીવું"], sub="આજથી જ નાના ફેરફાર શરૂ કરો."),
    dict(type="tip", v=0, icon="moon", title=f"રાત્રે {H}8 વાગ્યા{E}<br>પહેલાં જમો",
         body="હળવું અને વહેલું ડિનર — સવારે પેટ સાફ અને શરીર હળવું.", pair="Light dinner, happy gut"),
    dict(type="spotlight", v=0, kicker="રસોડાની દવા", title=f"{H}આદુ{E} — પાચનનો સાથી", big="Ginger", big_size=84, big_sub="આદુ",
         body="આદુ પાચન અને ગેસ માટે વર્ષોથી ઘરગથ્થુ ઉપાય તરીકે વપરાય છે."),
    dict(type="faq", v=2, title="Digest Powder નો સ્વાદ કેવો છે?",
         body="વરિયાળી flavour — હળવો અને તાજગીભર્યો. જમ્યા પછી લેવામાં એકદમ સરળ."),
    dict(type="quote", v=1, title=f"જેવું ખાશો,<br>{H}તેવું જીવશો{E}", body="You are what you eat — અને જે પચાવો છો!", pair="Digest better"),
    dict(type="myth", v=2, title="ગેસ માટે<br>Soda જ ઉપાય?", myth="ગેસ-acidity થાય તો soda કે cold drink પીવાથી રાહત મળે.",
         fact="Cold drinks થી ગેસ વધી શકે છે. હુંફાળું પાણી અને સંતુલિત ભોજન વધુ સારો વિકલ્પ છે."),
    dict(type="steps", v=2, kicker="Gut-Friendly Routine", title=f"સારા પાચન માટે<br>{H}3 આદત{E}",
         steps=["ધીમે ધીમે ચાવીને જમો", "જમ્યા પછી 10 મિનિટ ચાલો", "Digest Powder — હુંફાળા પાણી સાથે"]),
    dict(type="cta", v=0, kicker="પાચન માટે ખાસ", title=f"Arogyam+<br>{H}Digest Powder{E}",
         items=["Plant-Based", "વરિયાળી Flavour", "100g Pack", "Gas માં રાહત", "Acidity માં રાહત", "સરળ ઉપયોગ"]),
    # ---- cycle 3
    dict(type="hero", v=1, tag="Festive Care", kicker="તહેવારોની મોસમ", title=f"મીઠાઈ પછી પણ<br>{H}હળવું પેટ{E}",
         sub="તહેવારોમાં પાચનનો સાથી",
         items=[["stomach", "ભારેપણું ઓછું"], ["flame", "Acidity Relief"], ["leaf", "Natural Ingredients"], ["star", "Enjoy Festivals"]],
         badges=["વરિયાળી Flavour", "Plant-Based"]),
    dict(type="fact", v=1, title=f"પાચનની શરૂઆત {H}મોઢામાંથી{E} થાય છે",
         body="ખોરાકને સારી રીતે ચાવીને ખાવાથી તે પચવામાં સરળ બને છે — ઉતાવળ ન કરો."),
    dict(type="checklist", v=0, kicker="Constipation?", title=f"સવારે પેટ<br>{H}સાફ નથી થતું?{E}",
         items=["ઓછું પાણી", "ખોરાકમાં ઓછું fiber", "બેઠાડુ જીવન", "અનિયમિત ભોજન"], sub="આ કારણો પર ધ્યાન આપો."),
    dict(type="tip", v=2, icon="water", title=f"સવારે ઊઠીને<br>{H}હુંફાળું પાણી{E}",
         body="ખાલી પેટે 1-2 ગ્લાસ હુંફાળું પાણી પાચનતંત્રને સક્રિય કરવામાં મદદરૂપ છે.", pair="Morning gut care"),
    dict(type="spotlight", v=1, kicker="દરેક ઘરનો ઉપાય", title=f"{H}જીરું{E} — પાચનનો મસાલો", big="Jeera", big_size=96, big_sub="જીરું",
         body="જીરું પાચન માટે પરંપરાગત રીતે વપરાતો મસાલો છે — જીરા પાણી ઘણા ઘરોમાં રોજ પીવાય છે."),
    dict(type="faq", v=0, title="Digest Powder કોણ લઈ શકે?",
         body="ગેસ, એસિડિટી, ભારેપણું કે અપચાથી પરેશાન પુખ્ત વયના લોકો. ગર્ભાવસ્થા કે બીમારી હોય તો ડૉક્ટરની સલાહ લો."),
    dict(type="quote", v=0, title=f"પેટ ખુશ,<br>{H}તો તમે ખુશ!{E}", body="આજે તમારા પેટનો ખ્યાલ રાખો.", pair="Happy gut, happy you"),
    dict(type="myth", v=1, title="ભૂખ ન લાગે તો<br>જમવું જ નહીં?", myth="ભૂખ ન લાગે તો ભોજન છોડી દેવું સારું.",
         fact="વારંવાર ભોજન છોડવાથી acidity વધી શકે છે — નિયમિત સમયે હળવું ભોજન લો."),
    dict(type="steps", v=0, kicker="Festive Digestion Tips", title=f"તહેવારમાં<br>{H}પેટ સંભાળો{E}",
         steps=["મીઠાઈ-ફરસાણ માપસર", "ભોજન વચ્ચે પૂરતો gap", "જમ્યા પછી Digest Powder"]),
    dict(type="cta", v=2, kicker="FSSAI મંજૂર • Plant-Based", title=f"પાચનનો<br>{H}Perfect સાથી{E}",
         items=["Gas માં રાહત", "Acidity માં રાહત", "પેટ હળવું", "ભૂખ વધારે", "કબજિયાતમાં સહાયક", "દૈનિક પાચન"]),
]

PROD_LINES = {
    "sb": ["🧡 Niroza Sea Buckthorn Capsules — Vitamin A, B, C, E, K અને Omega 3, 6, 7, 9 નો કુદરતી સ્ત્રોત.",
           "🧡 Niroza Sea Buckthorn — Immunity, Skin Glow અને Hair Strength માટે રોજનું પોષણ.",
           "🧡 Himalaya ની Sea Buckthorn બેરીની શક્તિ — હવે Niroza ની Veg Capsules માં."],
    "b12": ["💚 Niroza Plant-Based Vitamin B12 — Moringa, Amla અને Barley Grass સાથે.",
            "💚 Niroza Vitamin B12 — Energy અને Nerve Health માટે 100% Plant-Based સાથ.",
            "💚 Vegetarian છો? Niroza Plant-Based B12 તમારા રોજના પોષણ માટે."],
    "dg": ["🌿 Arogyam+ Digest Powder — ગેસ, એસિડિટી અને ભારેપણામાં રાહત માટે આયુર્વેદ આધારિત.",
           "🌿 Arogyam+ Digest Powder — વરિયાળી flavour સાથે પાચનનો Perfect સાથી.",
           "🌿 જમ્યા પછી 1 ચમચી Arogyam+ Digest Powder — હળવું પેટ, ખુશ મન."],
}
TAGS = {
    "sb": ["#Niroza", "#NirozaAyurvedic", "#SeaBuckthorn", "#ImmunityBoost", "#SkinGlow", "#HairCare", "#Omega7", "#VitaminC",
           "#NaturalWellness", "#HealthyLifestyle", "#GujaratiHealth", "#Superfruit", "#Nutraceutical", "#Surat", "#Gujarat"],
    "b12": ["#Niroza", "#NirozaAyurvedic", "#VitaminB12", "#PlantBased", "#EnergyBoost", "#NerveHealth", "#Vegan", "#Moringa",
            "#Amla", "#HealthyLifestyle", "#GujaratiHealth", "#Vegetarian", "#Wellness", "#Surat", "#Gujarat"],
    "dg": ["#Niroza", "#NirozaAyurvedic", "#Arogyam", "#DigestPowder", "#GutHealth", "#AcidityRelief", "#GasRelief", "#HealthyDigestion",
           "#Ayurveda", "#AyurvedicHealth", "#GujaratiHealth", "#NaturalWellness", "#Surat", "#Gujarat", "#Pachan"],
}
EMO = {"hero": "🌿", "fact": "💡", "checklist": "🤔", "tip": "✅", "spotlight": "🔍", "faq": "❓",
       "quote": "✨", "myth": "🚫", "steps": "📝", "cta": "🛒"}


def plain(s):
    return re.sub(r"<br\s*/?>", " ", re.sub(r"<(?!br)[^>]+>", "", s or "")).replace("  ", " ").strip()


def caption(p, n, prod):
    L = []
    if p.get("kicker"):
        L.append(f"{EMO[p['type']]} {plain(p['kicker'])}")
        L.append(f"{plain(p['title'])}")
    else:
        L.append(f"{EMO[p['type']]} {plain(p['title'])}")
    L.append("")
    t = p["type"]
    if t == "hero":
        if p.get("sub"): L.append(p["sub"]); L.append("")
        L += [f"✔️ {it[1]}" for it in p["items"]]
    elif t in ("fact", "tip", "spotlight", "quote"):
        L.append(plain(p.get("body", "")))
    elif t == "checklist":
        L += [f"👉 {it}" for it in p["items"]]
        L.append(""); L.append(plain(p.get("sub", "")))
    elif t == "faq":
        L.append(f"👉 {plain(p['body'])}")
    elif t == "myth":
        L.append(f"❌ માન્યતા: {plain(p['myth'])}")
        L.append(f"✅ હકીકત: {plain(p['fact'])}")
    elif t == "steps":
        L += [f"{i}️⃣ {plain(s)}" for i, s in enumerate(p["steps"], 1)]
    elif t == "cta":
        L += [f"✔️ {it}" for it in p["items"]]
    L.append("")
    L.append(PROD_LINES[prod][n % 3])
    L.append("")
    L.append("📞 ઓર્ડર માટે Call / WhatsApp: +91 72111 69006")
    L.append("🚚 હોમ ડિલિવરી ઉપલબ્ધ • 📩 અથવા DM કરો")
    L.append("")
    L.append("ℹ️ આ ન્યુટ્રાસ્યુટિકલ પ્રોડક્ટ છે, દવા નથી. કોઈ બીમારી હોય તો ડૉક્ટરની સલાહ લો.")
    L.append("")
    tags = TAGS[prod]
    L.append(" ".join(tags[:3] + [tags[3 + (n + k) % (len(tags) - 3)] for k in range(7)]))
    return "\n".join(L).strip()


def build():
    out = []
    for day in range(30):
        for prod, arr in (("sb", SB), ("b12", B12), ("dg", DG)):
            p = dict(arr[day])
            p["product"] = prod
            p["id"] = f"{day + 1:02d}-{prod}"
            p["caption"] = caption(p, day, prod)
            out.append(p)
    return out


if __name__ == "__main__":
    posts = build()
    root = Path(__file__).resolve().parent.parent
    (root / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(posts), "posts")
