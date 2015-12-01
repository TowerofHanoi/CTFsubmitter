# Submitter service

you will need an instance of the web service which will receive the flags:
```
python submitter.py
```
and an instance of the worker which will submit the flags out:
```
python worker.py
```

## Requirements

+  bottle
+  pymongo>=3.0

for RuCTFe:

+  pwntools

for iCTF:

+  ictf



# Stats service

you will need another virtualenv since actually motor doesn't wrap pymongo 3

```
python stats.py
```

## Requirements

+  tornado
+  motor
