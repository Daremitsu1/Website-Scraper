import tkinter as tk
import time
import tkinter.messagebox as TMsg
from PIL import ImageTk
from tkinter import TOP, BOTH, X, LEFT
from tkinter.ttk import Frame
from selenium import webdriver
from bs4 import BeautifulSoup as bs 
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from Screenshot import Screenshot_Clipping 
import urllib.request
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
import pandas as pd

def code_enforcer(folionumber):
    options = webdriver.ChromeOptions()
    options.headless = True
    #set chromedriver.exe path 
    driver = webdriver.Chrome('bin/driver/chromedriver.exe')
    driver.maximize_window()
    #Launch Url
    driver.get('https://www2.miami-dadeclerk.com/cef/CitationSearch.aspx')
 
    folio_button = driver.find_element_by_link_text('Folio').click()
    folio_number = folionumber

    driver.implicitly_wait(30)

    #Find elements and take snapshots
    elementID = driver.find_element_by_css_selector("input[class*='form-control'][name='ctl00$ContentPlaceHolder1$txtFolioNumber']")
    elementID.send_keys(folio_number)

    elementID = driver.find_element_by_css_selector("input[id*='btnFolioSearch'][name='ctl00$ContentPlaceHolder1$btnFolioSearch']").click()
    
    driver.execute_script("document.body.style.zoom='50%'")
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    # Creating directory if not exists
    if not os.path.exists('CitationSearch'):
        os.makedirs('CitationSearch')

    driver.find_element_by_tag_name('body').screenshot(os.getcwd()+"/CitationSearch/"+folio_number+".png")
    #driver.get_screenshot_as_file(os.getcwd()+"/CitationSearch/"+folio_number+".png")
    driver.execute_script("document.body.style.zoom='100%'")

    page = bs(driver.page_source, features="html.parser")
    content = page.find_all('a',{'class':"btn btn-link pointer"})
    check_folio_srh_err = page.find_all('span',{'id':"lblSearchError"})
    if len(check_folio_srh_err)>0:
        return [404, "Folio Not Found, Please try again"]
    myinfo = []

    for info in content:
        myinfo.append(info.get('href'))

    templist = []

    for x in range(0, len(myinfo)):
        data = str(x+1)
        strSelector = "a[title*='View Citation Information"
        strSelectorEnd = "']"
        finalSelector = strSelector+data+strSelectorEnd
        driver.find_element_by_css_selector(finalSelector).click()
        

        status = driver.execute_script('return arguments[0].childNodes[5].textContent;', WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span#lblCitationHeader")))).strip()
        total_due = driver.execute_script('return arguments[0].lastChild.textContent;', WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span#lblCitationHeader")))).strip()
        issue_dept = driver.find_element_by_xpath('.//*[@id="form1"]/div[4]/div[9]/div/div/div[2]/table/tbody/tr[5]/td[2]').text
        lien_placed = driver.find_element_by_xpath('.//*[@id="lblLienPlaced"]').text

        driver.find_element_by_css_selector("a[id*='LinkButton1']").click()

        Table_dict = {
            'Status': status,
            'Total Due': total_due,
            'Issuing Department': issue_dept,
            'Lien_Placed': lien_placed
            }

        templist.append(Table_dict)
        df = pd.DataFrame(templist)



    df.to_csv(os.getcwd() + "/CitationSearch/" + folio_number + ".csv")
    return [200, "YAY! Scrapping done."]

def specialAssessment(folionumber):
    driver = webdriver.Chrome('bin/driver/chromedriver.exe')
    driver.maximize_window()
    driver.get('https://gisweb.miamidade.gov/SPTXLienLetters/')
    driver.find_element_by_xpath('//*[@id="divSplashScreenContent"]/table/tbody/tr[2]/td/div/div').click()

    folio_number = folionumber
    driver.implicitly_wait(30)

    #Find elements and take snapshots
    elementID = driver.find_element_by_xpath('//*[@id="txtAddress"]')
    elementID.send_keys(folio_number)



    elementID = driver.find_element_by_xpath('//*[@id="tdDivAddress"]/table/tbody/tr/td[2]').click()
    time.sleep(3)
    page = bs(driver.page_source, features="html.parser")
    check_folio_srh_err = page.find_all('div',{'id':"divMessage"})
    # print(check_folio_srh_err)
    # return
    if len(check_folio_srh_err)>0 and str(check_folio_srh_err[0].text).strip()!="":
        return [404, check_folio_srh_err[0].text]
    
    elementID = driver.find_element_by_xpath('//*[@id="trOtherAppLinks"]/td/div/span[1]/a').click()
 

    all_handles = driver.window_handles
    driver.switch_to.window(all_handles[1])
    
    pdf_browser = driver.current_url
    if not os.path.exists('SpecialAssessment'):
        os.makedirs('SpecialAssessment')
    download_path = os.getcwd() + '/SpecialAssessment/' + folio_number + ".pdf"
    pdfname = folio_number + ".pdf"
    urllib.request.urlretrieve(pdf_browser, download_path)
    # print(check_folio_srh_err)
    # Open a new window
    # driver.execute_script("window.open('');")
    # Switch to the new window
    driver.switch_to.window(all_handles[0])

    elementID = driver.find_element_by_xpath('//*[@id="trOtherAppLinks"]/td/div/span[2]/a').click()
    all_handles = driver.window_handles
    driver.switch_to.window(all_handles[2])

    urlSpecialAssessment = driver.current_url

    driver.get(urlSpecialAssessment)

    ob=Screenshot_Clipping.Screenshot()
    impPath = os.getcwd() + '/SpecialAssessment/'
    # img=ob.full_Screenshot(driver,save_path=impPath,image_name=folio_number + ".png")

    # https://www8.miamidade.gov/Apps/PA/PAOnlineTools/Taxes/NonAdvalorem.aspx?folio=0131230371470
    driver.save_screenshot(impPath+folio_number + ".png")
    # driver.save_screenshot(impPath+folio_number + "-1.png")

    return [200, "YAY! Scrapping done."]

def permitside(folio_number):
    #set chromedriver.exe path 
    driver = webdriver.Chrome('bin/driver/chromedriver.exe')
    driver.maximize_window()

    #Launch Url
    driver.get('https://www.miamidade.gov/permits/')

    current_windows = driver.current_window_handle
    #Click on Building Permits
    driver.find_element_by_xpath('//*[@id="leftNavigation"]/div[1]/ol/li[1]/span/a').click()

    all_handles = driver.window_handles
    driver.switch_to.window(all_handles[1])
    # print('Switch to new tab has been successful.')

    driver.find_element_by_xpath('/html/body/table/tbody/tr/td/form/table/tbody/tr[16]/td/input').click()

    # folio_number = '3022180000010'

    
    driver.implicitly_wait(30)

    #Find elements and take snapshots
    elementID = driver.find_element_by_css_selector("input[name*='inKey']")
    elementID.send_keys(folio_number)

    elementID = driver.find_element_by_xpath('/html/body/table/tbody/tr/td/form/input[1]').click()

    driver.implicitly_wait(30)

    #Find elements and take snapshots
    elementID = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/form/table[1]/tbody/tr/td/table/tbody/tr/td[2]/input')
    elementID.send_keys(folio_number)

    driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/form/table[2]/tbody/tr/td[2]/font/input').click()
    time.sleep(1)
    page = bs(driver.page_source, features="html.parser")
    check_folio_srh_err = page.find_all('font',{'id':"errorText"})
    if not os.path.exists('PermitSide'):
        os.makedirs('PermitSide')
    if len(check_folio_srh_err)>0 and str(check_folio_srh_err[0].text).strip()!="":
        driver.save_screenshot(os.getcwd()+ '/PermitSide/' + folio_number + "_error.png")
        return [404, check_folio_srh_err[0].text]
    
    
    driver.save_screenshot(os.getcwd()+ '/PermitSide/' + str(folio_number) + ".png")

    driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[1]/td[2]/p/b/font/a').click()

    #Switch to window 2
    current_windows = driver.current_window_handle
    all_handles = driver.window_handles
    driver.switch_to.window(all_handles[2])

    driver.save_screenshot(os.getcwd()+ '/PermitSide/' + folio_number + "_1.png")
    driver.quit
    return [200, "YAY! Scrapping done."]

def additional_code_enforcer(folio_number):
    driver = webdriver.Chrome('bin/driver/chromedriver.exe')
    driver.maximize_window()

    #Launch Url
    driver.get('https://gisweb.miamidade.gov/CodeViolations')
    try:
        WebDriverWait(driver, 602).until(EC.presence_of_element_located((By.ID, 'esri_dijit_Search_0_input')))
        skipbutton = driver.find_element_by_css_selector("button[class='jimu-btn jimu-float-trailing enable-btn lastFocusNode'][title='Continue'][aria-label='Continue']").click()
        page = bs(driver.page_source, features="html.parser")
        block_elem = page.find_all('div',{'id':"jimu_dijit_ViewStack_0"})
        if len(block_elem)>0:
            driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]').click()

        codeValElem = driver.find_element_by_css_selector('div[title="Open Code Violations Summary"][settingid="widgets_InfoSummary_Widget_18"]')
        if 'jimu-state-selected' in codeValElem.get_attribute('class').split():
            driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div[10]/div[1]/div[2]/div[3]').click()

        driver.implicitly_wait(30)

        elementID = driver.find_element_by_xpath('//*[@id="esri_dijit_Search_0_input"]')
        elementID.send_keys(folio_number)

        driver.find_element_by_xpath('//*[@id="esri_dijit_Search_0"]/div/div[2]').click()

        #Take snapshots
        driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(5)
        display_prop = driver.find_element_by_class_name("noResultsMenu").value_of_css_property('display')
        page = bs(driver.page_source, features="html.parser")
        no_result_block = page.find_all('div',{'class':"esriCTNoFeatureFound"})
        print(no_result_block)
        if display_prop == 'none' and len(no_result_block)==0:
            try: 
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'dijit_layout_ContentPane_2')))
            except:
                print("Seconadary Time Out")  
            if not os.path.exists('AddnlCodeEnforcement'):
                os.makedirs('AddnlCodeEnforcement')
            time.sleep(2)
            driver.save_screenshot(os.getcwd() + "/AddnlCodeEnforcement/" + str(folio_number) + ".png")
            return [200, "YAY! Scrapping done."]
        else:
            if not os.path.exists('AddnlCodeEnforcement'):
                os.makedirs('AddnlCodeEnforcement')
            driver.save_screenshot(os.getcwd() + "/AddnlCodeEnforcement/" + str(folio_number) + "_error.png")
            return [404, "No Result Found"]

    except Exception as e:
        return [404, "Time Out"]




def startScrapping():  
    folionumber=folio_no.get()
    # folionumber = '0131230371470'
    # folionumber = '01312303714'
    # folionumber = '0131230975540'
    #Validation for if user presses the button with empty text box or with any alphbatical inputs
    selectedOption = dade_type.get()
    if selectedOption == str(4):
        if folionumber == "":
            TMsg.showerror(title="Error", message="Please enter a folio number")
            os.exit()
    else:
        if folionumber == "":
            TMsg.showerror(title="Error", message="Please enter a folio number")
            os.exit()
        elif folionumber.isdecimal()==False:
            TMsg.showerror(title="Error", message="Please enter a folio number")
            os.exit()
        elif len(str(folionumber))<13 or len(str(folionumber))>13:
            TMsg.showerror(title="Error", message="Please enter a 13 digit folio number")
            os.exit()

    #print(selectedOption)
    
    if selectedOption == str(1):
        getFinalState = code_enforcer(folionumber)
    elif selectedOption == str(2):
        getFinalState = specialAssessment(folionumber)
    elif selectedOption == str(3):
        getFinalState = permitside(folionumber)
    elif selectedOption == str(4):
        getFinalState = additional_code_enforcer(folionumber)
    
    if getFinalState[0] == 404:
        TMsg.showerror(title="Error", message=getFinalState[1])
    elif getFinalState[0] == 200:
        TMsg.showinfo(title="Success", message=getFinalState[1])



app = tk.Tk()  
app.geometry("550x150")  
photo = ImageTk.PhotoImage(file="bin/nexvallogo.jpg")
app.iconphoto(False, photo)

frame0 = Frame(app)
frame0.pack(fill=X, pady=10, padx=10)

frame1 = Frame(app)
frame1.pack(fill=X, pady=10, padx=10)

folio_no=tk.StringVar()
dade_type = tk.StringVar(frame0, "1")
app.title('Miami Dade Title Search')

folio_number_lbl = tk.Label(frame1, text = 'Insert Folio No./Address', font=('calibre',10, 'bold'))
# folio_number_lbl.pack(side=LEFT)
folio_number_lbl2 = tk.Label(frame1, text = 'Insert Folio No', font=('calibre',10, 'bold'))
folio_number_lbl2.pack(side=LEFT)
folio_number_input = tk.Entry(frame1,textvariable = folio_no, font=('calibre',10,'normal'))
# folio_number_input.pack(fill=X, expand=False)
folio_number_input2 = tk.Entry(frame1,textvariable = folio_no, font=('calibre',10,'normal'))
folio_number_input2.pack(fill=X, expand=False)
def toggleLabels():
    selectedOption = dade_type.get()
    
    if selectedOption == str(4):
        folio_number_lbl.pack(side=LEFT)
        folio_number_input.pack(fill=X, expand=False)
        folio_number_lbl2.pack_forget()
        folio_number_input2.pack_forget()
    else:
        folio_number_lbl2.pack(side=LEFT)
        folio_number_input2.pack(fill=X, expand=False)
        folio_number_lbl.pack_forget()
        folio_number_input.pack_forget()


values = {"Code Enforcer" : "1",
          "Special Assessment" : "2",
          "Permit Side" : "3",
          "Additional Code Enforcement" : "4"}

for (text, value) in values.items():
    tk.Radiobutton(frame0, text = text, variable = dade_type, command= lambda : toggleLabels(),
                value = value).pack(side = LEFT, ipady = 5)

frame = Frame(app)
frame.pack(fill=BOTH, expand=True, pady=10)
scrap_init_btn = tk.Button(frame,text = "Start Scrapping",command=lambda : startScrapping(),activeforeground = "green",pady=20)  
scrap_init_btn.pack(side=TOP)

app.mainloop()  