import gspread

try:
    gc = gspread.service_account(filename='gen-lang-client-0965804770-1b0674d6e028.json')
    sh = gc.open_by_key('1SFRlXmO_xmcD1HGnMN4LmALch2tkKGNlGFoOHtu5VYM')
    
    titles = [ws.title for ws in sh.worksheets()]
    print("SUCCESS")
    print("Tabs:", titles)
except Exception as e:
    print("ERROR", repr(e))
