from flask import Flask, request #, jsonify
from libfptr10 import IFptr
import datetime
#from threading import Thread
#from pybase64 import b64decode
#import os
#from dotenv import load_dotenv
#import time
#import telebot

app = Flask(__name__)

# version 24.02.28.1
# ------------------
#KASSA_IP ='192.0.0.154'
#KASSA_IP = os.getenv('KASSA_IP')


def initializationKKT(connectType, ip_kassy, inn_company):
        # инициализация драйвера
        fptr = IFptr("")
   
        # подключение ККТ
        if connectType == "TCP/IP":
            settings = {
                IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
                IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP, #\\\\\\\\\\\\ Для подключения к кассе по TCP/IP
                IFptr.LIBFPTR_SETTING_IPADDRESS: ip_kassy, #\\\\\\\\\\\\ Для подключения к кассе по TCP/IP
                IFptr.LIBFPTR_SETTING_IPPORT: 5555 #\\\\\\\\\\\\ Для подключения к кассе по TCP/IP
            }
        if connectType == "Удаленный ПК":
            settings = {
                IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
                IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_USB, #\\\\\\\\\\\\ Для удаленного подключения к кассе через ПК
                IFptr.LIBFPTR_SETTING_REMOTE_SERVER_ADDR: ip_kassy #\\\\\\\\\\\\ Для удаленного подключения к кассе через ПК
            }
        if connectType == "USB":
            settings = {
                IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
                IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_USB, #\\\\\\\\\\\\ Для подключения к кассе по USB
            }

        fptr.setSettings(settings)
        fptr.open()
        isOpened = fptr.isOpened()
        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
        fptr.fnQueryData()
        if isOpened==1 and inn_company != fptr.getParamString(1018).strip():
            isOpened = 9 # ИНН ККТ не соответсвует ИНН Организации (код ошибки - 9)
        print('Статус готовности к обмену с ККТ: '+ str(isOpened))    
        return isOpened, fptr
    
def checkReceiptClosed():
        while fptr.checkDocumentClosed() < 0:   # не удалось проверить состояние документа.
            print(fptr.errorDescription())
            continue
        CheckClosed = True
        if not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):  # документ не закрылся, отменяем.
            fptr.cancelReceipt()
            CheckClosed = False
            print("Чек отменен!")
            botMessage = "Неудачная обработка чека"
            bot.send_message(user_id, botMessage)
        print("Результат операции: " + fptr.errorDescription())       
        return CheckClosed
    
def checkOfMarring(markingCodeBase64):

        markingCode = (b64decode(markingCodeBase64)).decode()
        fptr.setParam(IFptr.LIBFPTR_PARAM_MARKING_CODE_TYPE, IFptr.LIBFPTR_MCT12_AUTO)
        fptr.setParam(IFptr.LIBFPTR_PARAM_MARKING_CODE, markingCode)
        fptr.setParam(IFptr.LIBFPTR_PARAM_MARKING_CODE_STATUS, 2)   # товар в стадии реализации
        fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, 1.000)
        fptr.setParam(IFptr.LIBFPTR_PARAM_MEASUREMENT_UNIT, IFptr.LIBFPTR_IU_PIECE)
        fptr.setParam(IFptr.LIBFPTR_PARAM_MARKING_PROCESSING_MODE, 0)
        fptr.beginMarkingCodeValidation()

        # дожидаемся окончания проверки и запоминаем результат
        while True:
            fptr.getMarkingCodeValidationStatus()
            if fptr.getParamBool(IFptr.LIBFPTR_PARAM_MARKING_CODE_VALIDATION_READY):
                break
        validationResult = fptr.getParamInt(IFptr.LIBFPTR_PARAM_MARKING_CODE_ONLINE_VALIDATION_RESULT)

        # подтверждаем реализацию товара с указанным КМ
        fptr.acceptMarkingCode()
        print("КМ товара прошел проверку - ", markingCode)

        return markingCode, validationResult
    
def jsonDisassembly(content):
    # разбор контейнера json
    ip_kassy = content['ip_kassy']
    inn_company = content['inn_сompany']
    operator = content['operator']
    num_predpisania = content['num_predpisania']
    clientInfo = content['clientInfo']
    rnm = content['rnm']
    fn = content['fn']
    adress = content['adress']
    fd_number = content['fd_number']
    fd_type = content['fd_type']
    corr_type = content['corr_type']
    sign_calc = content['sign_calc']
    check_data = content['check_data']
    shift_number = content['shift_number']
    check_sum = content['check_sum']
    check_cash = content['check_cash']
    check_electron = content['check_electron']
    check_prepay = content['check_prepay']
    check_prepay_offset = content['check_prepay_offset']
    check_postpay = content['check_postpay']
    barter_pay = content['barter_pay']
    sum_NO_VAT = content['sum_NO_VAT']
    sum_0_VAT = content['sum_0_VAT']
    sum_10_VAT = content['sum_10_VAT']
    sum_18_VAT = content['sum_18_VAT']
    sum_20_VAT = content['sum_20_VAT']
    sum_110_VAT = content['sum_110_VAT']
    sum_120_VAT = content['sum_120_VAT']
    doc_osn = content['doc_osn']
    sno = content['sno']
    inn_operator = content['inn_operator']
    check_print = content['check_print']
    itemsQuantity = len(content['items'])
    
    return ip_kassy, inn_company, operator, num_predpisania, clientInfo, rnm, fn, adress,fd_number, fd_type, corr_type, sign_calc, check_data, shift_number, check_sum, check_cash, check_electron, check_prepay, check_prepay_offset, \
    check_postpay, barter_pay, sum_NO_VAT, sum_0_VAT, sum_10_VAT, sum_18_VAT, sum_20_VAT, sum_110_VAT, sum_120_VAT, doc_osn, sno, inn_operator, check_print, itemsQuantity

def jsonItemsDisassembly(item):
    item_number = item['item_number']
    item_name = item['item_name']
    item_sign_sub_calc = item['item_sign_sub_calc']
    item_price = item['item_price']
    item_quantity = item['item_quantity']
    item_sum = item['item_sum']
    sign_way_calc = item['sign_way_calc']
    item_mera = item['item_mera']
    t1200_VAT_no = item['t1200_VAT_no']
    t1200_VAT_0 = item['t1200_VAT_0']
    t1200_VAT_10 = item['t1200_VAT_10']
    t1200_VAT_18 = item['t1200_VAT_18']
    t1200_VAT_20 = item['t1200_VAT_20']
    t1200_VAT_110 = item['t1200_VAT_110']
    t1200_VAT_120 = item['t1200_VAT_120']
    sign_agent = item['sign_agent']
    tel_OP = item['tel_OP']
    transaction_BPA = item['transaction_BPA']
    tel_PA = item['tel_PA']
    tel_OPP = item['tel_OPP']
    name_OP = item['name_OP']
    adress_OP = item['adress_OP']
    inn_OP = item['inn_OP']
    data_supplier = item['data_supplier']
    inn_supplier = item['inn_supplier']
    dop_rekvizit = item['dop_rekvizit']
    return item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, sign_way_calc, item_mera, t1200_VAT_no, t1200_VAT_0, t1200_VAT_10, t1200_VAT_18, t1200_VAT_20, \
    t1200_VAT_110, t1200_VAT_120, sign_agent, tel_OP, transaction_BPA, tel_PA, tel_OPP, name_OP, adress_OP, inn_OP, data_supplier, inn_supplier, dop_rekvizit

def productRegistration(item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, sign_way_calc, item_mera, t1200_VAT_no, t1200_VAT_0, t1200_VAT_10, t1200_VAT_18, \
    t1200_VAT_20, t1200_VAT_110, t1200_VAT_120, sign_agent, tel_OP, transaction_BPA, tel_PA, tel_OPP, name_OP, adress_OP, inn_OP, data_supplier, inn_supplier, dop_rekvizit, sno, fptr):  
    fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, item_name)
    fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, item_price)
    fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, item_quantity)
    if item_mera == 71:     # единица измеренения - час
        fptr.setParam(IFptr.LIBFPTR_PARAM_MEASUREMENT_UNIT, IFptr.LIBFPTR_IU_HOUR)
    else:                   # единица измеренения - штука
        fptr.setParam(IFptr.LIBFPTR_PARAM_MEASUREMENT_UNIT, IFptr.LIBFPTR_IU_PIECE)

    if sno == 1:
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)    # для ПР НДС - 20% (ОСН)
        fptr.setParam(IFptr.LIBFPTR_PARAM_USE_ONLY_TAX_TYPE, True)
    else:
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_NO)  # для ПР - НДС не облагается (не ОСН)

    if (item_number != 1) and (item_sign_sub_calc == 10):
        sign_way_calc = 3

    fptr.setParam(1214, sign_way_calc)  # признак способа расчета: полный расчет (4), аванс (3)
    fptr.setParam(1212, item_sign_sub_calc) # предмет расчета: товар (1), услуга (4), платеж (7)
    fptr.registration()
    return

def checkReceiptClosed(fptr):
    
    while fptr.checkDocumentClosed() < 0:   # не удалось проверить закрытие чека
        print(fptr.errorDescription())
        continue
    if fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):
        CheckClosed = True
        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_LAST_DOCUMENT)
        fptr.fnQueryData()
        fiscalSign          = fptr.getParamString(IFptr.LIBFPTR_PARAM_FISCAL_SIGN)
        dateTime            = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
        print("Фискальные данные чека: ", fiscalSign, " ", dateTime)
    elif not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):  # чек не закрылся,- отменяем его
        fptr.cancelReceipt()
        CheckClosed = False
    print("Результат закрытия чека: " + fptr.errorDescription())       
    return CheckClosed, fiscalSign, dateTime

@app.route("/")
def root():
    #bot.send_message(user_id, "Тест")
    return "PCS KKT ATOL SERVER (5034)"

@app.route("/checkProcessing", methods = ['POST'])
def loadCheck():
    # Старт обработки тела чека
    content = request.json
    connectType = content['connect']

    if content['operator'] == 'service-ping':
        ip_kassy = content['ip_kassy']
        inn_company = content['inn_сompany']
        connectStatus, fptr = initializationKKT(connectType, ip_kassy, inn_company)   # инициализация и подключение ККТ
        status = 2                  # по умолчанию - касса не готова !
        fiscalSign = ""
        dateTime = ""
        if connectStatus == 1:      # касса готова
            status = 1
        if connectStatus == 9:      # ИНН не ИНН !
            status = 9
        return str(status) + "=" + fiscalSign + "=" + str(dateTime)
    
    if content['operator'] == 'service-X-report':
        ip_kassy = content['ip_kassy']
        inn_company = content['inn_сompany']
        connectStatus, fptr = initializationKKT(connectType, ip_kassy, inn_company)   # инициализация и подключение ККТ
        status = 2                  # по умолчанию - касса не готова !
        fiscalSign = ""
        dateTime = ""
        if connectStatus == 1:      # касса готова
            status = 1
            fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
            fptr.report()
        if connectStatus == 9:      # ИНН не ИНН !
            status = 9
        return str(status) + "=" + fiscalSign + "=" + str(dateTime)

    ip_kassy, inn_company, operator, num_predpisania, clientInfo, rnm, fn, adress, fd_number, fd_type, corr_type, sign_calc, check_data, shift_number, check_sum, check_cash, check_electron, check_prepay, \
    check_prepay_offset, check_postpay, barter_pay, sum_NO_VAT, sum_0_VAT, sum_10_VAT, sum_18_VAT, sum_20_VAT, sum_110_VAT, sum_120_VAT, doc_osn, sno, inn_operator, check_print, itemsQuantity = jsonDisassembly(content)
    
    connectStatus, fptr = initializationKKT(connectType, ip_kassy, inn_company)   # инициализация и подключение ККТ  
    if connectStatus == 1:      # ККТ готова

        fiscalSign = '0'
        dateTime = '0'

        fptr.setParam(1021, operator) # кассир
        fptr.operatorLogin()

        # Развилка: простой чек или чек коррекции?
        if fd_type == 1: # кассовый чек
            #fptr.setParam(1062, sno)    # применяемая система налогообложения      # ОШИБКА ПРИ ИСПОЛЬЗОВАНИИ !!!
            if sign_calc == 1:
                fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)        # ПРИХОД
            if sign_calc == 2:
                fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_RETURN) # ВОЗВРАТ ПРИХОДА
            if sign_calc == 3:
                fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_BUY )        # РАСХОД
             

        if fd_type == 2: # чек коррекции
            #fptr.setParam(1062, sno)    # применяемая система налогообложения      # ОШИБКА ПРИ ИСПОЛЬЗОВАНИИ !!!

            fptr.setParam(1178, datetime.datetime(int(check_data[6:10]), int(check_data[3:5]), int(check_data[:2])))  # нужны, если по предписанию ФНС
            fptr.setParam(1179, num_predpisania) # нужны, если по предписанию ФНС
            fptr.utilFormTlv() # нужны, если по предписанию ФНС
            correctionInfo = fptr.getParamByteArray(IFptr.LIBFPTR_PARAM_TAG_VALUE)  # нужны, если по предписанию ФНС

            if sign_calc == 1:
                fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_CORRECTION)   # КОРРЕКЦИЯ ПРИХОДА
            if sign_calc == 2:
                fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_RETURN_CORRECTION)   # КОРРЕКЦИЯ ВОЗВРАТА ПРИХОДА
            if sign_calc == 3:
                fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_BUY_CORRECTION )        # КОРРЕКЦИЯ РАСХОДА
             
            fptr.setParam(1173, 0)  # тип коррекции - самостоятельно (по предписанию - 1)
            fptr.setParam(1174, correctionInfo) # составной реквизит, состоит из "1178" и "1179"
            fptr.setParam(1192, str(doc_osn))

        # дальше - общее и для чека и для коррекции
        fptr.setParam(1008, clientInfo) # данные клиента (приходит пустая строка)
        if not check_print:
            fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY, True) # чек не печатаем
        fptr.openReceipt()

        i = 0
        while i < itemsQuantity:
            item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, sign_way_calc, item_mera, t1200_VAT_no, t1200_VAT_0, t1200_VAT_10, t1200_VAT_18, t1200_VAT_20, \
            t1200_VAT_110, t1200_VAT_120, sign_agent, tel_OP, transaction_BPA, tel_PA, tel_OPP, name_OP, adress_OP, inn_OP, data_supplier, inn_supplier, dop_rekvizit = jsonItemsDisassembly(content['items'][i]) 
            productRegistration(item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, sign_way_calc, item_mera, t1200_VAT_no, t1200_VAT_0, t1200_VAT_10, t1200_VAT_18, t1200_VAT_20, \
            t1200_VAT_110, t1200_VAT_120, sign_agent, tel_OP, transaction_BPA, tel_PA, tel_OPP, name_OP, adress_OP, inn_OP, data_supplier, inn_supplier, dop_rekvizit, sno, fptr) # регистрация каждого товара в чеке  
            i += 1

        if check_cash > 0:
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH) # наличная оплата
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, check_cash)
            fptr.payment()
        if check_electron > 0:
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY) # безналичная оплата
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, check_electron)
            fptr.payment()

        # if check_prepay > 0:
        #    fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_PREPAID) # аванс
            
        if check_postpay > 0:   
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CREDIT) # кредит
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, check_postpay)
            fptr.payment()

        if check_prepay_offset > 0:
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_PREPAID) # зачет предоплаты (аванса)
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, check_prepay_offset)
            fptr.payment()

        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, sum_20_VAT)
        fptr.receiptTax()

        fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, check_sum)
        fptr.receiptTotal()
        
        fptr.closeReceipt()     # закрытие чека
        CheckClosed, fiscalSign, dateTime = checkReceiptClosed(fptr)    # обработка результата операции
        status = 0
        if CheckClosed:
            status = 1
        fptr.close()

    elif connectStatus == 9:
        status = 9
        fiscalSign = ""
        dateTime = ""
        print("ИНН ККТ не соответствует ИНН организации!")   
    else:
        status = 2
        fiscalSign = ""
        dateTime = ""
        print("КАССА ЗАНЯТА!")
    return str(status) + "=" + fiscalSign + "=" + str(dateTime)

@app.route("/testKkt")
def testKkt():
    # Инициализация драйвера
    fptr = IFptr("")
    version = fptr.version()

    print('version')
    print(version)

    # Подключение ККТ
    settings = {
        IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
        IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
        IFptr.LIBFPTR_SETTING_IPADDRESS: "192.0.0.153",
        IFptr.LIBFPTR_SETTING_IPPORT: 5555
    }
    fptr.setSettings(settings)

    fptr.open()
    isOpened = fptr.isOpened()
    print('isOpened')
    fptr.lineFeed()
    print(isOpened)
    # return 'version: ' + str(version)

    # Закрытие смены
    fptr.setParam(fptr.LIBFPTR_PARAM_REPORT_ELECTRONICALLY, 1)

    fptr.setParam(1021, "Кассир Иванов И.")
    fptr.setParam(1203, "123456789047")
    fptr.operatorLogin()

    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
    fptr.report()

    #fptr.setParam(IFptr.LIBFPTR_PARAM_PRINT_REPORT, False)
    #fptr.deviceReboot()

    return 'Cмена закрыта'

@app.route("/testOFD")
def testOFD():
    # Инициализация драйвера
    fptr = IFptr("")
    version = fptr.version()
    print('version')
    print(version)
    # Подключение ККТ
    settings = {
        IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
        IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
        IFptr.LIBFPTR_SETTING_IPADDRESS: "192.0.0.153",
        IFptr.LIBFPTR_SETTING_IPPORT: 5555
    }
    fptr.setSettings(settings)
    fptr.open()
    isOpened = fptr.isOpened()
    print('isOpened')
    print(isOpened)
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_TEST)
    fptr.report()

    return 'OK'

@app.route("/get_INN")
def get_INN():
    # Инициализация драйвера
    fptr = IFptr("")
    version = fptr.version()
    print('version')
    print(version)
    # Подключение ККТ
    settings = {
        IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
        IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
        IFptr.LIBFPTR_SETTING_IPADDRESS: "192.0.0.153",
        IFptr.LIBFPTR_SETTING_IPPORT: 5555
    }
    fptr.setSettings(settings)
    fptr.open()
    isOpened = fptr.isOpened()
    print('isOpened')
    print(isOpened)
    fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
    fptr.fnQueryData()
    INN = fptr.getParamString(1018)
    print('ИНН ', INN)
    return INN

    # Подключение ККТ
    settings = {
        IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
        IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
        IFptr.LIBFPTR_SETTING_IPADDRESS: "192.0.0.153",
        IFptr.LIBFPTR_SETTING_IPPORT: 5555
    }
    fptr.setSettings(settings)

    fptr.open()
    isOpened = fptr.isOpened()
    print('isOpened')
    fptr.lineFeed()
    print(isOpened)
    # return 'version: ' + str(version)

    # Закрытие смены
    fptr.setParam(fptr.LIBFPTR_PARAM_REPORT_ELECTRONICALLY, 1)

    fptr.setParam(1021, "Кассир Иванов И.")
    fptr.setParam(1203, "123456789047")
    fptr.operatorLogin()

    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
    fptr.report()

    #fptr.setParam(IFptr.LIBFPTR_PARAM_PRINT_REPORT, False)
    #fptr.deviceReboot()

    return 'Cмена закрыта'

    

app.run("0.0.0.0", 5034)