# הכנה לראיון — Oracle ERP Cloud Financials

בנק שאלות ותשובות: פונקציונלי, טכני והתנהגותי. השתמש כדי לתרגל, לא לשנן מילה במילה.

---

## חלק 1 — פונקציונלי / חשבונאי

**ש: הסבר את זרימת ה-Record to Report (R2R) ב-Oracle Fusion.**
עסקאות נקלטות ב-Subledgers (AP/AR/FA וכו') → **SLA** ממפה אותן לפי חוקי חשבונאות
ליומני GL → Posting ל-GL → Period Close (Revaluation, Translation, Allocations,
Consolidation) → דוחות (OTBI/FRS/Smart View).

**ש: מהו Subledger Accounting (SLA) ולמה הוא חשוב?**
מנוע שממיר עסקאות תפעוליות לרשומות חשבונאיות לפי כללים מוגדרים (Accounting Rules).
מאפשר מדיניות חשבונאית גמישה ומרובת-תקנים (Multi-GAAP) בלי לשנות את מקור העסקה.

**ש: הסבר את מבנה ה-Enterprise Structure ו-Chart of Accounts.**
Legal Entities, Ledgers (Primary/Secondary), Balancing/Reporting Segments,
Value Sets, Cross-Validation Rules. COA = מבנה הסגמנטים (למשל Company, Cost Center,
Account, Product...). הדגש חשיבות תכנון נכון כי קשה לשנות אחרי go-live.

**ש: מה קורה ב-Period Close?**
סגירת subledgers → העברה ל-GL → Revaluation (הערכת מטבע חוץ) → Translation
(תרגום למטבע דיווח) → Allocations → Consolidation (ב-FCCS) → סגירת התקופה →
דוחות. ציין reconciliation בין subledger ל-GL.

**ש: ההבדל בין Primary ל-Secondary Ledger?**
Primary = ה-ledger הראשי לישות. Secondary = ledger מקביל למטרות דיווח/תקן חשבונאי
אחר (למשל local GAAP מול IFRS), מוזן ע"י Journal/Subledger/Balance level.

**ש: איך מבוצע Intercompany ואיזון (balancing)?**
Intercompany Balancing Rules יוצרים אוטומטית שורות איזון בין ישויות כדי לשמור
על ledger מאוזן בכל balancing segment.

---

## חלק 2 — טכני / כלים

**ש: מתי OTBI ומתי BI Publisher?**
- **OTBI** — ניתוח אד-הוק ודשבורדים אינטראקטיביים מעל subject areas מובנים.
- **BIP (BI Publisher)** — דוחות מעוצבים/פורמליים (חשבוניות, דוחות רגולטוריים),
  שאילתות SQL ישירות למסד, פורמטים (PDF/Excel), scheduling.

**ש: מה זה FBDI ומתי משתמשים בו?**
File-Based Data Import — טעינת נתונים בכמות (המרות, פתיחת יתרות, יבוא חשבוניות)
דרך תבניות Excel → CSV → ZIP → Import process. לשימוש בהמרות ובעדכונים מסיביים.

**ש: איך מחלצים/מעדכנים נתונים בכמות מלבד FBDI?**
ADFdi spreadsheets, REST/SOAP APIs, ה-BI Publisher לחילוץ, ו-HDL בצד HCM.

**ש: מה זה Smart View?**
תוסף Excel המתחבר ל-GL/EPM (FCCS/EPBCS) לשליפה, ניתוח ותכנון מתוך אקסל.
נפוץ מאוד ל-FP&A ולדיווח הנהלה.

**ש: איך מתמודדים עם Quarterly Updates של Oracle Cloud?**
Oracle מפיצה עדכונים רבעוניים חובה. תהליך: קריאת Release Notes → בדיקת השפעה
(impact assessment) → רגרסיה ב-Test env → אישור → החלה ל-Production. הדגש בקרת שינויים.

**ש: מה זה FCCS/ARCS/EPBCS?**
FCCS = Consolidation & Close. ARCS = Account Reconciliation. EPBCS = Planning,
Budgeting & Forecasting. כולם חלק מ-Oracle EPM Cloud ומשלימים את ה-ERP.

---

## חלק 3 — התנהגותי (STAR)

ענה במבנה **STAR**: Situation, Task, Action, Result.

> **STAR** = שיטת מבנה לתשובה: מה היה המצב, מה הייתה המשימה שלך, מה עשית, ומה התוצאה
> (רצוי מכומתת). מונע תשובות מעורפלות.

שאלות נפוצות להכין להן סיפור STAR מוכן:
- ספר על סגירה/הטמעה שהצלת תחת לחץ זמן.
- מקרה של אי-התאמה (reconciliation gap) — איך אבחנת ופתרת.
- קונפליקט מול משתמש עסקי / מול צוות טכני — איך גישרת.
- שיפור תהליך שהובלת ומה החיסכון.
- טעות שעשית ומה למדת ממנה.

---

## שאלות לשאול את המראיין

- באיזה שלב אתם עם Oracle Cloud (הטמעה / BAU / הרחבה)?
- אילו מודולים בשימוש והיכן הכאב הכי גדול היום?
- מבנה הצוות והחלוקה בין functional ל-technical?
- איך מנוהלים ה-Quarterly Updates אצלכם?

---

## צ'קליסט יום לפני

- [ ] חזרה על המודולים הרלוונטיים למשרה הספציפית
- [ ] 5-6 סיפורי STAR מוכנים ומכומתים
- [ ] מונחים מדויקים (SLA, FBDI, OTBI, Period Close) על קצה הלשון
- [ ] מחקר על החברה — באיזה Oracle Cloud היא משתמשת אם ידוע
- [ ] 3-4 שאלות למראיין
- [ ] סביבה ל-remote: מצלמה, אור, אינטרנט, שקט
