import OpenDartReader

"""한국 전자공시 시스템 API
https://github.com/FinanceData/OpenDartReader
"""

api_key = ""

dart = OpenDartReader(api_key)
dart.company("애자일소다")
dart.list("애자일소다")
dart.sub_docs("20230331000907", match="재무")
