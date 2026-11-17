# هشت خطای عمدی و دام رفتاری

این قطعه‌ها را مستقل اجرا کنید. بعضی خطاها منطقی‌اند و استثنا ندارند؛ متن کامل traceback به نسخه و مسیر وابسته است و خروجی ثابت فصل محسوب نمی‌شود.
## E01 — درخواست پس از پایان

```python
source = iter([])
next(source)
```

نتیجهٔ مورد انتظار: استثنای `StopIteration`.

next بدون پیش‌فرض در پایان این استثنا را اعلام می‌کند. این مثال خطای نحوی نیست.

راه اصلاح: از حلقهٔ for یا next با نشانهٔ مناسب استفاده کنید؛ پایان طبیعیِ مولد را با return بنویسید.

## E02 — دو بار مصرف یک منبع

```python
source = iter([10, 20])
print(sum(source))
print(sum(source))
```

نتیجهٔ مورد انتظار: بدون استثنا، اما دارای دام منطقی.

خروجی پیش از پایان یا خطا:

```text
30
0
```

هیچ استثنایی رخ نمی‌دهد، ولی نتیجهٔ دوم به سؤال اولیه جواب نمی‌دهد.

راه اصلاح: دو شاخص را در یک گذر محاسبه کنید یا ورودی محدود را آگاهانه ذخیره کنید.

## E03 — ناسازگاری طول در zip

```python
pairs = zip(["A", "B"], [1], strict=True)
print(next(pairs))
print(next(pairs))
```

نتیجهٔ مورد انتظار: استثنای `ValueError`.

خروجی پیش از پایان یا خطا:

```text
('A', 1)
```

زوج نخست پیش از تشخیص کمبود منبع دوم تولید شده است؛ strict تضمین تراکنش نیست.

راه اصلاح: اثر جانبیِ هر زوج را پیش از اطمینان از قرارداد کنترل کنید. strict هم‌ترازی کلیدها را ثابت نمی‌کند.

## E04 — فهرست مشترک در سطح کلاس

```python
class Batch:
    notes = []
first = Batch()
second = Batch()
first.notes.append("checked")
print(second.notes)
```

نتیجهٔ مورد انتظار: بدون استثنا، اما دارای دام منطقی.

خروجی پیش از پایان یا خطا:

```text
['checked']
```

هر دو نمونه فهرست یکسانِ کلاسی را می‌بینند.

راه اصلاح: برای یادداشت مستقل، self.notes = [] را در __init__ قرار دهید.

## E05 — مولد وابسته به فایل بسته

```python
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "input.txt"
    path.write_text("one", encoding="utf-8")
    with path.open(encoding="utf-8") as source:
        lines = (line.strip() for line in source)
    print(next(lines))
```

نتیجهٔ مورد انتظار: استثنای `ValueError`.

بدنهٔ عبارت مولد بعد از خروج از with سراغ فایل می‌رود؛ فایل بسته است.

راه اصلاح: مصرف را داخل with انجام دهید، یا with را داخل مولد قرار دهید و بستن زودهنگامش را مدیریت کنید.

## E06 — انتظار خطای فوری از مولد

```python
def checked(size):
    if size <= 0:
        raise ValueError("invalid size")
    yield size
source = checked(0)
print("created")
next(source)
```

نتیجهٔ مورد انتظار: استثنای `ValueError`.

خروجی پیش از پایان یا خطا:

```text
created
```

اعتبارسنجی بدنه تا زمان مصرف به تأخیر افتاده است.

راه اصلاح: اگر خطای فوری لازم است، تابع بیرونی معمولی بنویسید که پس از اعتبارسنجی مولد داخلی را بسازد.

## E07 — بازنویسی فیلد frozen

```python
from dataclasses import dataclass
@dataclass(frozen=True)
class Amount:
    gross: int
amount = Amount(100)
amount.gross = 200
```

نتیجهٔ مورد انتظار: استثنای `FrozenInstanceError`.

انتساب معمول به فیلد frozen ممنوع است.

راه اصلاح: شیء تازه بسازید یا مدل تغییرپذیر مناسبی انتخاب کنید؛ frozen تضمین اعتبار عددی یا تغییرناپذیری عمیق نیست.

## E08 — اشتباه‌گرفتن راهنمای نوع با اعتبارسنجی

```python
from dataclasses import dataclass
@dataclass
class Amount:
    gross: int
amount = Amount("wrong")
print(type(amount.gross).__name__)
```

نتیجهٔ مورد انتظار: بدون استثنا، اما دارای دام منطقی.

خروجی پیش از پایان یا خطا:

```text
str
```

راهنمای int در زمان اجرای معمول، سازنده را به اعتبارسنج خودکار تبدیل نکرده است.

راه اصلاح: برای قرارداد لازم، کنترل زمان اجرا یا ابزار اعتبارسنجیِ آگاهانه نیاز است. این فصل چارچوب عمومی ارائه نمی‌کند.

