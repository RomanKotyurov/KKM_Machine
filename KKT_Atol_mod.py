from flask import Flask, request, jsonify
from libfptr10 import IFptr
from threading import Thread
#from pybase64 import b64decode
#import os
#from dotenv import load_dotenv
#import time
#import datetime
#import telebot

app = Flask(__name__)

#KASSA_IP ='192.0.0.154'
#KASSA_IP = os.getenv('KASSA_IP')


def initializationKKT():
        # инициализация драйвера
        fptr = IFptr("")
        #version = fptr.version()
        #print('driver version:  ' + str(version))
   
        # подключение ККТ
        settings = {
            IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
            IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
            IFptr.LIBFPTR_SETTING_IPADDRESS: "192.0.0.154", # 153, 154
            IFptr.LIBFPTR_SETTING_IPPORT: 5555
        }
        fptr.setSettings(settings)
        fptr.open()
        isOpened = fptr.isOpened()
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
    uuid = content['uuid']
    operator = content['operator']
    num_predpisania = content['num_predpisania']
    clientInfo = content['clientInfo']
    fp = content['fp']
    rnm = content['rnm']
    fn = content['fn']
    adress = content['adress']
    fd_number = content['fd_number']
    fd_type = content['fd_type']
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
    sum_20_VAT = content['sum_20_VAT']
    sum_110_VAT = content['sum_110_VAT']
    sum_118_VAT = content['sum_118_VAT']
    sum_120_VAT = content['sum_120_VAT']
    sign_way_calc = content['sign_way_calc']
    sign_agent = content['sign_agent']
    inn_supplier = content['inn_supplier']
    name_supplier = content['name_supplier']
    itemsQuantity = len(content['items'])
    return uuid, operator, num_predpisania, clientInfo, fp, rnm, fn, adress,fd_number, fd_type, sign_calc, check_data, shift_number, check_sum, check_cash, check_electron, check_prepay, check_prepay_offset, \
    check_postpay, barter_pay, sum_NO_VAT, sum_0_VAT, sum_10_VAT, sum_20_VAT, sum_110_VAT, sum_118_VAT, sum_120_VAT, sign_way_calc, sign_agent, inn_supplier, name_supplier, itemsQuantity

def jsonItemsDisassembly(item):
    item_number = item['item_number']
    item_name = item['item_name']
    item_sign_sub_calc = item['item_sign_sub_calc']
    item_price = item['item_price']
    item_quantity = item['item_quantity']
    item_sum = item['item_sum']
    item_VAT_rate = item['item_VAT_rate']
    item_VAT_sum = item['item_VAT_sum']
    return item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, item_VAT_rate, item_VAT_sum



    if isOpened == 1:
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
        fptr.queryData()
        state = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE)
        if (state == 2):
            fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY, True)
            fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
            fptr.report()
    return isOpened, fptr

def productRegistration(item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, item_VAT_rate, item_VAT_sum, fptr):  
    fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, item_name)
    fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, item_price)
    fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, item_quantity)
    fptr.setParam(IFptr.LIBFPTR_PARAM_MEASUREMENT_UNIT, IFptr.LIBFPTR_IU_PIECE) # единица измеренения - штука
    fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_NO)  # НДС не облагается
    fptr.setParam(1214, 4)  # признак способа расчета - полный расчет (4) (зависит от <sign_way_calc>)
    #codPriznakaPredmetaRascheta = priznakPredmetaRascheta(item_sign_sub_calc)
    fptr.setParam(1212, item_sign_sub_calc) # предмет расчета
    fptr.registration()
    return

def checkReceiptClosed(fptr):
    while fptr.checkDocumentClosed() < 0:   # не удалось проверить закрытие чека
        print(fptr.errorDescription())
        continue
    CheckClosed = True
    if not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):  # чек не закрылся,- отменяем его
        fptr.cancelReceipt()
        CheckClosed = False
        botMessage = "! Неудачная обработка чека"
        #bot.send_message(GROUP_ID, botMessage)
    print("Результат закрытия чека: " + fptr.errorDescription())       
    return CheckClosed

@app.route("/")
def root():
    #bot.send_message(user_id, "Тест")
    return "PCS KKT ATOL SERVER (5034)"

@app.route("/checkProcessing", methods = ['POST'])
def loadCheck():
    # Старт обработки тела чека
    content = request.json
    #botMessage = str(content)
    #botMessage = "--> получен чек коррекции"
    #bot.send_message(user_id, botMessage)
    uuid, operator, num_predpisania, clientInfo, fp, rnm, fn, adress, fd_number, fd_type, sign_calc, check_data, shift_number, check_sum, check_cash, check_electron, check_prepay, check_prepay_offset, \
    check_postpay, barter_pay, sum_NO_VAT, sum_0_VAT, sum_10_VAT, sum_20_VAT, sum_110_VAT, sum_118_VAT, sum_120_VAT, sign_way_calc, sign_agent, inn_supplier, name_supplier, itemsQuantity = jsonDisassembly(content)
    
    connectStatus, fptr = initializationKKT()   # инициализация и подключение ККТ  
    if connectStatus == 1:      # ККТ готова

        fptr.setParam(1021, operator) # кассир
        fptr.operatorLogin()

        #fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL) # ПОТОМ УБРАТЬ!

        fptr.setParam(1178, datetime.datetime(int(check_data[:4]), int(check_data[5:7]), int(check_data[8:10])))  # 
        fptr.setParam(1179, num_predpisania)
        fptr.utilFormTlv()
        correctionInfo = fptr.getParamByteArray(IFptr.LIBFPTR_PARAM_TAG_VALUE)
        sign_calc = sign_calc
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_CORRECTION)   # КОРРЕКЦИЯ ПРИХОДА (зависит от sign_calc)
        fptr.setParam(1173, 1)  # тип коррекции (самостоятельно или по предписанию), связан с параметром "1179"
        fptr.setParam(1174, correctionInfo) # составное реквизит, состоит из "1178" и "1179" 
        fptr.setParam(1008, clientInfo) # данные клиента
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY, True) # чек не печатаем
        fptr.openReceipt()

        i = 0
        while i < itemsQuantity:
            item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, item_VAT_rate, item_VAT_sum = jsonItemsDisassembly(content['items'][i]) 
            productRegistration(item_number, item_name, item_sign_sub_calc, item_price, item_quantity, item_sum, item_VAT_rate, item_VAT_sum, fptr) # регистрация каждого товара в чеке  
            i += 1

        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY) # LIBFPTR_PT_ELECTRONICALLY - безналичная оплата
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, check_sum)
        fptr.payment()
        fptr.closeReceipt()     # закрытие чека

        CheckClosed = checkReceiptClosed(fptr)    # обработка результата операции
        status = 0
        if CheckClosed:
            status = 1
        fptr.close()

    else:
        status = 2
        print("КАССА ЗАНЯТА!")

    return str(status)

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