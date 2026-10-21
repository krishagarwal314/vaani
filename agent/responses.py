"""Scripted lines used by deterministic recovery paths and by the offline MockLLM."""
from __future__ import annotations

LENDER = "Sahayak Finance"

T: dict[str, dict[str, str]] = {
    "greeting": {
        "en": "Hello, am I speaking with {name}?",
        "hinglish": "Namaste, kya meri baat {name} ji se ho rahi hai?",
        "hi": "नमस्ते, क्या मेरी बात {name} जी से हो रही है?",
    },
    "consent": {
        "en": f"Hi {{name}}, this is Vaani calling from {LENDER} about a pre-approved personal loan offer. "
              "This call is recorded for quality purposes. Do you have two minutes?",
        "hinglish": f"{{name}} ji, main Vaani bol rahi hoon {LENDER} se, aapke pre-approved personal loan "
                    "offer ke baare mein. Yeh call quality ke liye record ho rahi hai. Kya aapke paas do minute hain?",
        "hi": f"{{name}} जी, मैं {LENDER} से वाणी बोल रही हूँ, आपके प्री-अप्रूव्ड पर्सनल लोन ऑफर के बारे में। "
              "यह कॉल क्वालिटी के लिए रिकॉर्ड हो रही है। क्या आपके पास दो मिनट हैं?",
    },
    "need_discovery": {
        "en": "Great. How much loan are you looking for, and what is it for?",
        "hinglish": "Badhiya. Aapko kitne loan ki zaroorat hai, aur kis cheez ke liye?",
        "hi": "बढ़िया। आपको कितने लोन की ज़रूरत है, और किस चीज़ के लिए?",
    },
    "ask_employment_type": {
        "en": "Are you salaried or self-employed?",
        "hinglish": "Aap salaried hain ya self-employed?",
        "hi": "आप नौकरी करते हैं या अपना काम?",
    },
    "ask_monthly_income": {
        "en": "What is your monthly take-home income?",
        "hinglish": "Aapki monthly in-hand income kitni hai?",
        "hi": "आपकी महीने की इन-हैंड आमदनी कितनी है?",
    },
    "ask_existing_emi": {
        "en": "Are you paying any EMIs right now? If yes, how much per month in total?",
        "hinglish": "Kya abhi aap koi EMI bhar rahe hain? Agar haan, toh total kitni har mahine?",
        "hi": "क्या अभी आप कोई EMI भर रहे हैं? अगर हाँ, तो कुल कितनी हर महीने?",
    },
    "offer": {
        "en": "Good news, you are eligible for {amount} at {rate} percent for {tenure} months. "
              "Your EMI would be {emi} a month. Shall we go ahead?",
        "hinglish": "Achhi khabar, aap {amount} ke liye eligible hain, {rate} percent par {tenure} mahine ke liye. "
                    "Aapki EMI {emi} mahina hogi. Kya hum aage badhein?",
    },
    "offer_confirm": {
        "en": "Shall we go ahead with this offer?",
        "hinglish": "Kya hum is offer ke saath aage badhein?",
    },
    "objection_rate": {
        "en": "I understand. The rate is fixed for the full tenure with no hidden charges, and a longer "
              "tenure brings the EMI down. Would you like to go ahead?",
        "hinglish": "Main samajh sakti hoon. Rate poore tenure ke liye fixed hai, koi hidden charges nahi, "
                    "aur lamba tenure lene se EMI kam ho jaati hai. Kya aage badhein?",
    },
    "objection_existing_loan": {
        "en": "That's fine. Your current EMIs are already counted in this offer, and many customers use it "
              "to consolidate costlier loans. Would you like to go ahead?",
        "hinglish": "Koi baat nahi. Aapki current EMIs is offer mein pehle se count hain, aur kaafi customers "
                    "ise mehenge loans consolidate karne ke liye use karte hain. Kya aage badhein?",
    },
    "objection_family": {
        "en": "Of course, it's a big decision. I can call back once you've discussed it with your family. "
              "Should I schedule that?",
        "hinglish": "Bilkul, yeh bada decision hai. Family se baat karne ke baad main call kar sakti hoon. "
                    "Callback schedule kar doon?",
    },
    "objection_trust": {
        "en": f"That's very fair. We will never ask for your OTP, PIN or password. You can also apply directly "
              f"on the official {LENDER} app. Would you like to go ahead?",
        "hinglish": f"Bilkul sahi baat hai. Hum kabhi aapka OTP, PIN ya password nahi maangenge. Aap seedha "
                    f"{LENDER} ke official app par bhi apply kar sakte hain. Kya aage badhein?",
    },
    "objection_generic": {
        "en": "I understand. May I ask what's holding you back, the rate, the EMI, or something else?",
        "hinglish": "Main samajh sakti hoon. Kya main pooch sakti hoon kya rok raha hai, rate, EMI, ya kuch aur?",
    },
    "commitment": {
        "en": "Would you like to apply now? I'll send a secure link to your registered number. "
              "Or should I schedule a callback?",
        "hinglish": "Kya aap abhi apply karna chahenge? Main aapke registered number par secure link bhej "
                    "doongi. Ya callback schedule kar doon?",
    },
    "applied": {
        "en": "Wonderful. I've sent the application link by SMS. It takes about five minutes to complete.",
        "hinglish": "Bahut badhiya. Maine application link SMS kar diya hai. Paanch minute lagenge.",
    },
    "callback_ask": {
        "en": "Sure. What time works best for a callback?",
        "hinglish": "Zaroor. Aapko kis time call karoon?",
        "hi": "ज़रूर। आपको किस समय कॉल करूँ?",
    },
    "callback_booked": {
        "en": "Done, I'll call you {when}.",
        "hinglish": "Ho gaya, main aapko {when} call karungi.",
    },
    "callback_bad_time": {
        "en": "We can only call between 9 AM and 9 PM. What time in that window works for you?",
        "hinglish": "Hum sirf subah 9 se raat 9 baje ke beech call kar sakte hain. Us beech kaunsa time theek rahega?",
    },
    "callback_unclear": {
        "en": "Sorry, what day and time should I call you?",
        "hinglish": "Maaf kijiye, kis din aur kitne baje call karoon?",
    },
    "closing": {
        "en": "Thank you for your time, {name}. Have a great day!",
        "hinglish": "Aapke time ke liye shukriya, {name} ji. Aapka din shubh ho!",
        "hi": "आपके समय के लिए धन्यवाद, {name} जी। आपका दिन शुभ हो!",
    },
    "closing_wrong_person": {
        "en": "Sorry for the trouble. Have a good day!",
        "hinglish": "Takleef ke liye maafi. Aapka din shubh ho!",
    },
    "dnc_goodbye": {
        "en": "Understood. I've removed your number from our calling list. Sorry for the disturbance, goodbye.",
        "hinglish": "Samajh gayi. Maine aapka number calling list se hata diya hai. Disturb karne ke liye maafi.",
        "hi": "समझ गई। मैंने आपका नंबर कॉलिंग लिस्ट से हटा दिया है। परेशानी के लिए माफ़ी।",
    },
    "not_interested_goodbye": {
        "en": "No problem at all. Thank you for your time, have a good day!",
        "hinglish": "Koi baat nahi. Aapke time ke liye shukriya, din shubh ho!",
        "hi": "कोई बात नहीं। आपके समय के लिए धन्यवाद!",
    },
    "bot_disclosure": {
        "en": f"Yes, I'm Vaani, an AI assistant calling on behalf of {LENDER}. "
              "A human advisor can call you if you prefer.",
        "hinglish": f"Ji haan, main Vaani hoon, {LENDER} ki taraf se ek AI assistant. "
                    "Aap chahein toh ek human advisor aapko call kar sakte hain.",
        "hi": f"जी हाँ, मैं वाणी हूँ, {LENDER} की तरफ़ से एक AI असिस्टेंट। आप चाहें तो एक एडवाइज़र आपको कॉल कर सकते हैं।",
    },
    "off_topic": {
        "en": "Ha, fair enough! Coming back to your loan,",
        "hinglish": "Haha, sahi baat hai! Waise loan ki baat karein toh,",
    },
    "dead_air_reprompt": {
        "en": "Hello, are you still there?",
        "hinglish": "Hello, kya aap line par hain?",
        "hi": "हैलो, क्या आप लाइन पर हैं?",
    },
    "dead_air_goodbye": {
        "en": "Seems like this isn't a good time. I'll try again later. Goodbye!",
        "hinglish": "Lagta hai abhi sahi time nahi hai. Main baad mein try karungi. Dhanyavaad!",
    },
    "readback": {
        "en": "Just to confirm, {amount}?",
        "hinglish": "Bas confirm kar loon, {amount}, sahi hai?",
        "hi": "बस कन्फर्म कर लूँ, {amount}, सही है?",
    },
    "ask_amount_again": {
        "en": "Sorry about that. Could you tell me the amount again?",
        "hinglish": "Maaf kijiye. Amount ek baar phir bata dijiye?",
    },
    "sorry_repeat": {
        "en": "Sorry, I didn't catch that. Could you say it again?",
        "hinglish": "Maaf kijiye, samajh nahi aaya. Ek baar phir bolenge?",
        "hi": "माफ़ कीजिए, समझ नहीं आया। एक बार फिर बोलेंगे?",
    },
}


def render(key: str, lang: str, **kw: object) -> str:
    variants = T[key]
    text = variants.get(lang) or (variants.get("hinglish") if lang == "hi" else None) or variants["en"]
    return text.format(**kw)
