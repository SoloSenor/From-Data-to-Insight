# هشت خطای عمدی فصل ۱۱

این نمونه‌ها عمداً ناسالم‌اند؛ اجرای آن‌ها از پروژهٔ سالم جداست.

## E01 — اشتباه نحوی در متنِ برنامه

```python
compile("if True print('ready')", 'broken.py', 'exec')
```

شکست مورد انتظار: SyntaxError

اصلاح:

```python
if True:
    print('ready')
```

دونقطه و بلوک تورفته لازم است. متن ناسالم در رشته قرار دارد تا خود فایل آموزشی قابل import بماند. شکست compile عمداً در فرایند جدا آزموده می‌شود.

## E02 — پنهان‌نکردن TypeError

```python
int(['3'])
```

شکست مورد انتظار: TypeError

اصلاح:

```python
value = '3'
print(int(value))
```

اینجا نوع ورودی نادرست است، نه صرفاً متن غیرعددی؛ افزودن except عمومی اصلاح قرارداد نیست. فراخواننده باید نوع درست را ارسال کند یا مرز ورودی آن را صریح رد کند.

## E03 — مخرج صفر و شاخص تعریف‌نشده

```python
print(0 / 0)
```

شکست مورد انتظار: ZeroDivisionError

اصلاح:

```python
total = 0
share = None if total == 0 else 0 / total
print(share)
```

سهم در کل صفر، در قرارداد این کتاب تعریف‌نشده و None است؛ صفر درصد ادعای دیگری است. شاخص تعریف‌نشده را با خطای برنامه‌نویسی یکی نکنید.

## E04 — بلعیدن باگ با except عمومی

```python
def total():
    try:
        return missing_price * 2
    except Exception:
        return 0
print(total())
```

خروجی ناسالم:

```text
0
```

اصلاح:

```python
price = 100
print(price * 2)
```

NameError در نسخهٔ ناسالم به صفر ظاهراً معتبر تبدیل شده است. رفع نام متغیر و محدودکردن try راه‌حل است؛ صفر ساختگی، گزارش موفق نیست.

## E05 — return در finally و ناپدیدشدن شکست

```python
def read():
    try:
        raise ValueError("invalid input")
    finally:
        return 0
print(read())
```

خروجی ناسالم:

```text
0
```

اصلاح:

```python
events = []
def read():
    try:
        raise ValueError("invalid input")
    finally:
        events.append("cleaned")
try:
    read()
except ValueError:
    print("still failed", events)
```

return در finally استثنا را می‌پوشاند. finally را برای پاک‌سازی نگه دارید و اجازه دهید خطای اصلی منتشر شود. در نسخه‌های دیگر Python ممکن است هشدارهای اضافی برای این الگو وجود داشته باشد؛ محیط مرجع این فصل ۳.۱۱ است.

## E06 — کنترل ورودی فقط با assert

```python
import subprocess
import sys
code = "assert 0 > 0; print('accepted')"
result = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True)
print(result.stdout.strip())
```

خروجی ناسالم:

```text
accepted
```

اصلاح:

```python
quantity = 0
try:
    if quantity <= 0:
        raise ValueError('invalid quantity')
except ValueError:
    print('blocked')
```

حذف assert در حالت -O این ورودی را عبور می‌دهد. کنترل لازم‌الاجرا باید if و raise باشد؛ تست نهایی پروژه نیز در مفسر -O اجرا می‌شود.

## E07 — oracle همسان با برنامهٔ غلط

```python
def wrong(q, p, r):
    return q * p - r
expected = wrong(3, 100, 1)
print(wrong(3, 100, 1) == expected)
```

خروجی ناسالم:

```text
True
```

اصلاح:

```python
actual = 3 * 100 - 1
expected = 200
print(actual == expected)
```

تابع تحت آزمون نباید مرجع خودش باشد. در نسخهٔ اصلاح‌شده False نتیجهٔ مطلوبِ آشکارسازی باگ است؛ اصلاح فرمول باید بعد از آزمون شکست‌خورده انجام شود.

## E08 — تلورانس بزرگ که باگ را قبول می‌کند

```python
import math
print(math.isclose(299, 200, rel_tol=0.5))
```

خروجی ناسالم:

```text
True
```

اصلاح:

```python
actual = 299
expected = 200
print(actual == expected)
```

برای مبلغ صحیح تومان مقایسهٔ دقیق مناسب است. تلورانس ۵۰درصدی، باگ واضح را می‌پوشاند؛ انتخاب تلورانس باید از معنا، واحد و خطای قابل‌قبول بیاید.
