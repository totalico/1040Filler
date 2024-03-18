import os

from pypdf import PdfReader, PdfWriter
from Util import configObjToArray


forms = ['1040 - 2023']
output= configObjToArray('DIRS', '.editconfig')['output_folder'] + '\\'
outputEndix = "_2023.pdf"

def createOutputFolder ():
    if not os.path.exists(output):
        try:
            os.makedirs(output)
        except OSError as error:
            print(error)

def f8812 (schedulePath, scheduleFields ,f1040_l1 , f1040_l11 ,f1040_l18_tax ,s3_l1_1116 ,dependancesNum, conf='.\\.editconfig',outputfile =output + 'f8812' + outputEndix):

    childCredit = 2000
    additionalChildCredit = 1600
    otherStatuses=200000
    workSheetA = f1040_l18_tax - s3_l1_1116   #Tax there - Tax here
    if  workSheetA < 0:
        workSheetA = 0
    l5=dependancesNum*childCredit
    l16b = dependancesNum*additionalChildCredit

    fields = configObjToArray('FIELDS', scheduleFields)
    data   = configObjToArray('CALC_DATA', conf)
    personal_data = configObjToArray('FILLER_DETAILS', '.\\.editconfig')

    result = {}
    l13 = workSheetA
    _1040_l19=workSheetA
    if workSheetA > l5:
        _1040_l19= l5
    result['l19']= _1040_l19

    l16a = l5 - _1040_l19
    l17 = l16a
    if l16a > l16b:
        l17 = l16b
    l18a = f1040_l1
    l19 = l18a-2500
    l20 = int(l19*0.15)

    l25 = 0
    l26 = 0
    if l16b >= 4800:
        if l20 > l17:
            l27 = l17
        else:
            print('You need to fill in 8812 form Part II-B manually!')
            l27=l17
    else:
        print('In Form 8812 line 20: If are a bona fide resident of Puerto Rico, go and fill lines 21 - 26')
        if l20 > l17:
            l27 = l17
        else:
            l27 = l20

    result['l28']= l27


    reader = PdfReader(schedulePath)
    writer = PdfWriter()
    writer.append(reader)

    writer.update_page_form_field_values(
        writer.pages[0], {
            fields['name'] : personal_data['name'] +' '+ personal_data['family_name'],
            fields['ssn'] : personal_data ['ssn'],
            fields['l1_gross_income']:str (f1040_l11),
            fields['l2d_0']:'0',
            fields['l3__gross_income']: str (f1040_l11),
            fields['l4_num_children']:  str(dependancesNum),
            fields['l5_mult_l4_2000']: str(l5),
            fields['l6_non_qualified_children-0']:'0',
            fields['l7_mult_l6_500']: '0',
            fields['l8_add_l7_l5']: str(l5),
            fields['l9_status_200k']: str(otherStatuses),
            fields['l10_sub_from_l3_l9-0']: '0', #is wages > 200k ? I wish...
            fields['l11_mult_l10_0.05']: '0',
            fields['l12_sub_l8_l11']: str(l5), #as l8
            fields['l13_credit_limit_worksheet_a']: str (workSheetA),
            fields['l14-0']: str(_1040_l19),
        })

    writer.update_page_form_field_values(
        writer.pages[1], {
            fields['l16a_sub_l12_l14']:  str(l5 - _1040_l19), #as l8
            fields['l16b1_num_children']: str(dependancesNum),
            fields['l16b2_l16b1*1500']: str(l16b),
            fields['l17_smaller_l16a_l16b2']: str(l17), #nowadays cannot be otherwise
            fields['l18a_earned_income']: str(l18a),
            fields['l18b_combat_pay-0']: '0',
            fields['l19_l18a_isbigger_2500']:str(l19),
            fields['l20_mult_l19_by_0.15']:str(l20),
            fields['l21_medicare-0']: '0',
            fields['l22_s1l15-0']: '0',
            fields['l23_add_l22_21-0']: '0',
            fields['l24_2040l27-0']: '0',
            fields['l25_sub_l23_l24-0']: str(l25),
            fields['l26_bigger_l20_l25-l20']: str(l26),
            fields['l27_smaller_l26_l17-l17']: str(l27)

            })
    # write "Output-beta" to pypdf-Output-beta.pdf
    with open(outputfile, "wb") as output_stream:
        writer.write(output_stream)

    forms.append('form 8812')
    return result


'''
@qualifiedDivindends = line 3a
@amountTaxtable - line 15 in 1040.
@sched_D_smaller_l15_or_16 = schedule D line 15 [usually is zero, then it will be o] OR line 16

:return 1040 tax amount to entry space
'''
def calcTax(amountTaxtable_104l15, conf ='.\\.editconfig'):

    short_term = configObjToArray('SHORT_TERM', conf)
    long_term = configObjToArray('LONG_TERM', conf)
    dividents = configObjToArray('DIVIDENDS', conf)
    qualifiedDivindends =int( dividents['qualified_dividend'])
    sched_D_smaller_l15_or_16 = int(long_term['realized_gain'])

    if sched_D_smaller_l15_or_16 <= 0 and qualifiedDivindends <=0 :
        return int(getTaxFromTable(amountTaxtable_104l15))                  #has changed from 2022

    if  int(short_term['realized_gain']) < sched_D_smaller_l15_or_16:
        sched_D_smaller_l15_or_16=int(short_term['realized_gain'])

    l4 = qualifiedDivindends + sched_D_smaller_l15_or_16  # line4
    l5 = amountTaxtable_104l15 - l4

    tax_l5 = 0 #  dividndes gain
    if l5 < 0:
        l5 = 0

    headOfHousehold = 59750         #has changed from 2022
    l7 = headOfHousehold
    if amountTaxtable_104l15 < headOfHousehold:
        l7 = amountTaxtable_104l15
    l8 = l5
    if l7 < l5:
        l8 = l7
    l9 = l7 - l8
    l10 = amountTaxtable_104l15
    if l4 < amountTaxtable_104l15:
        l10 = l4
    l12 = l10 - l9
    l13 = 523050                    #has changed from 2022
    l14 = amountTaxtable_104l15
    if l13 < amountTaxtable_104l15:
        l14 = amountTaxtable_104l15
    l15 = l5 + l9
    l16 = l14 - l15
    if l16 < 0:
        l16 = 0
    l17 = l12
    if l16 < l12:
        l17 = l16
    l18 = l17 * 0.15
    l19 = l9 + l17
    l20 = l10 - l19
    l21 = l20 * 0.20

    if l5 > 100000:
        l22=TaxComputationWorksheet(l5)
    else:
        l22 = int(getTaxFromTable(l5))

    l23 = l18 + l21 + l22
    if amountTaxtable_104l15 < 100000:
        l24 = int(getTaxFromTable(amountTaxtable_104l15))
    else:
        l24 = TaxComputationWorksheet(amountTaxtable_104l15)
    l25 = l24
    if l23 > l24:
        l25 = l24

    worksheet = configObjToArray('OTHER_FORMS' , conf)['worksheet']
    with open(output + worksheet, 'w') as file:
        file.write('Line        |       value       \n')
        file.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        file.write('1           |       ' + str(amountTaxtable_104l15) + '  \n')
        file.write('4           |       ' + l4.__str__() + '       \n')
        file.write('5           |       ' + l5.__str__() + '       \n')
        file.write('7           |       ' + l7.__str__() + '       \n')
        file.write('8           |       ' + l8.__str__() + '       \n')
        file.write('9           |       ' + l9.__str__() + '       \n')
        file.write('10          |       ' + l10.__str__() + '       \n')
        file.write('12          |       ' + l12.__str__() + '       \n')
        file.write('13          |       ' + l13.__str__() + '       \n')
        file.write('14          |       ' + l14.__str__() + '       \n')
        file.write('15          |       ' + l15.__str__() + '       \n')
        file.write('16          |       ' + l16.__str__() + '       \n')
        file.write('17          |       ' + l17.__str__() + '       \n')
        file.write('18          |       ' + l18.__str__() + '       \n')
        file.write('19          |       ' + l19.__str__() + '       \n')
        file.write('20          |       ' + l20.__str__() + '       \n')
        file.write('21          |       ' + l21.__str__() + '       \n')
        file.write('22          |       ' + l22.__str__() + '       \n')
        file.write('23          |       ' + l23.__str__() + '       \n')
        file.write('24          |       ' + l24.__str__() + '       \n')
        file.write('25          |       ' + l25.__str__() + '       \n')

    print('Created summered file : ' + output + worksheet)
    return int(l25)


def getTaxFromTable(amount, ppInIstructionTable = 65):
    print('Regular Tax. check in tax table.')
    # TODO For future developing make the table automatically
    b= str(ppInIstructionTable)
    a = input('Insert amount from Tax-Table [instruction page: ' + b + ']  for income amount : ' + str(amount) + ' :> ' )
    return a

'''
Vary from year to year. Here is HOH only!
'''
def TaxComputationWorksheet(l15):
    print('Hi tax rate, over 100K. Needs speicel calculation:')
    match l15:
        case l15 if l15 < 182100 :
            print('1st grade of HOH')
            l15 = l15*0.24 - 8206
        case l15 if l15 < 231250:
            print('2st grade of HOH')
            l15 = l15 * 0.32 - 22774
        case l15 if l15 < 578100:
            print('3st grade of HOH')
            l15 = l15 * 0.35 - 29711.50
        case _: # greater than this amount.
            print('most grade of HOH')
            l15 = l15 * 0.37 - 41273
    return  l15




def form_1116(schedulePath, scheduleFields, schedule3Path, schedule3Fields, f1040_l15_taxtableAmount, f1040_l16_tax , conf = '.editconfig',outputfile = output +'f1116' + outputEndix):

    date = '1.1.23 - 12.31.23'                     #has changed from 2022
    data = configObjToArray('CALC_DATA', conf)
    fields = configObjToArray('FIELDS', scheduleFields)
    personal_data = configObjToArray('FILLER_DETAILS', conf)

    usd = float(data['ils_usd_rate'])
    salary_usd = int(float(data['salary_in_ils']) / usd)
    tax = int(float(data['tax_in_ils']) / usd )

    bituch_briut = int(float(data['bituch_briut_ils']) / usd)
    bituch_leumi = int(float(data['bituch_leumi_ils']) / usd)
    totalTaxUSD = tax + bituch_leumi + bituch_briut
    totalTaxILS = int(data['bituch_briut_ils']) + int(data['bituch_leumi_ils']) + int(data['tax_in_ils'])
    print(
        'in USD :\nTaxes = ' + str(tax) + '\nBituch-Briut = ' + str(bituch_briut) + '\nBituch-Leumi = ' + str(bituch_leumi) + '\nTotal = ' + str(totalTaxUSD))

    l7_taxtable_income = salary_usd - int(data['standard_deduction'])
    wages_incomes_ratio = l7_taxtable_income / f1040_l15_taxtableAmount
    l21 = int(f1040_l16_tax * wages_incomes_ratio)
    l24 = totalTaxUSD
    if l21 < totalTaxUSD:
        l24 = l21
    reader = PdfReader(schedulePath)
    writer = PdfWriter()
    writer.append(reader)

    writer.update_page_form_field_values(
        writer.pages[0], {
            fields['name']: personal_data['name'] + ' ' + personal_data['family_name'],
            fields['ssn']: personal_data['ssn'],
            fields['state_from']:personal_data['country'],
            fields['country']: personal_data['country'],
            fields['income_reason']: 'WAGES',
            fields['income_sum']: salary_usd,
            fields['total_income_sum']: salary_usd,
            fields['itimazed_deduction']: data['standard_deduction'],
            fields['sum_deduction']: data['standard_deduction'],
            fields['gross_income']: salary_usd,
            fields['gross_income_all_sources']: salary_usd,
            fields['divide_e_by_d']: '1' ,
            fields['mult_f_by_c']: data['standard_deduction'],
            fields['deduction_from_all']: data['standard_deduction'],
            fields['deduction_from_all_sum']: data['standard_deduction'],
            fields['wage_sub_deduction']: str(l7_taxtable_income),
            fields['date_range']: date,
            fields['forigen_texes_paid_ils']: str(totalTaxILS),
            fields['forigen_texes_paid_usd']: str(totalTaxUSD),
            fields['forigen_texes_paid_usd_sum']: str(totalTaxUSD),
            fields['forigen_texes_paid_usd_total']: str(totalTaxUSD)
        })
    writer.update_page_form_field_values(
        writer.pages[1], {
            fields['tax']: str(totalTaxUSD),
            fields['carry_over']: '0',
            fields['tax_carry']: str(totalTaxUSD),
            fields['combine_all_tax']: str(totalTaxUSD),
            fields['income_after_deduction']: str(l7_taxtable_income),
            fields['adjestment']: '0',
            fields['income_total']: str(l7_taxtable_income),
            fields['amount_in_1040_line_15']: str(f1040_l15_taxtableAmount),
            fields['div_income_by_line_15']: str(wages_incomes_ratio),
            fields['amount_in_1040_line_16']: str(f1040_l16_tax),
            fields['mult_l20_by_l19']: str(l21),
            fields['add_lines_20_21']: str(l21),
            fields['smaller_l14_or_l23']: str(l24),
            fields['from_l24']: str(l24),
            fields['boycott_reduction_always_0']: '0',
            fields['sum_to_1040_schedule_3_l2']: str(l24)

        })
    # write "Output-beta" to pypdf-Output-beta.pdf
    with open(outputfile, "wb") as output_stream:
        writer.write(output_stream)
    schedule_3(schedule3Path, schedule3Fields ,l24)
    forms.append('form 1116')
    return int(l24)

'''
line 8 - put in 1040 l_20
'''
def schedule_3(schedulePath, scheduleFields, _1116amount,outputfile =output + 'schedule3' + outputEndix):

    fields = configObjToArray('FIELDS', scheduleFields)

    personal_data = configObjToArray('FILLER_DETAILS', '.\\.editconfig')
    reader = PdfReader(schedulePath)
    writer = PdfWriter()
    writer.append(reader)

    writer.update_page_form_field_values(
        writer.pages[0], {
            fields['name']: personal_data['name'] + ' ' + personal_data['family_name'],
            fields['ssn']: personal_data['ssn'],
            fields['_1116form']: str(_1116amount),
            fields['total']: str(_1116amount)
        })
    # write "Output-beta" to pypdf-Output-beta.pdf
    with open(outputfile, "wb") as output_stream:
        writer.write(output_stream)
    forms.append('schedule 3')



# schedule D
def capitalGain(schedulePath, scheduleFields, conf =  '.editconfig' ,outputfile =output + 'scheduleD'+outputEndix):

    fields = configObjToArray('FIELDS', scheduleFields)

    data = configObjToArray('CALC_DATA', conf)
    personal_data = configObjToArray('FILLER_DETAILS', conf)
    short_terms = configObjToArray('SHORT_TERM', conf)
    long_term = configObjToArray('LONG_TERM', conf)

    totalGainShort = int(short_terms['realized_gain']) - int(short_terms['loss_carry_over'])
    totalGainLong = int(long_term['realized_gain']) - int(long_term['loss_carry_over'])
    totalShortAndLong = totalGainLong + totalGainShort

    if totalShortAndLong == 0 :
        print('No need in sced. D, No gain.')
        return 0

    reader = PdfReader(schedulePath)
    writer = PdfWriter()
    writer.append(reader)
    writer.update_page_form_field_values(
        writer.pages[0], {
            fields['name']: personal_data['name'] + ' ' + personal_data['family_name'],
            fields['ssn']: personal_data['ssn'],
            fields['proceed_short_term']: short_terms['proceeds'],
            fields['cost_short_term(basis)']: short_terms['cost_basis'],
            fields['gain_short_term']: short_terms['realized_gain'],

            fields['loss_carryover']: short_terms['loss_carry_over'],
            fields['sum_gain_carryover']: str(totalGainShort),

            fields['proceed_long_term']: long_term['proceeds'],
            fields['cost_long_term']: long_term['cost_basis'],
            fields['gain_long_term']: long_term['realized_gain'],

            fields['long_term_carryover']: long_term['loss_carry_over'],
            fields['sum_long_term_gain']: str(totalGainLong),

        })

    writer.update_page_form_field_values(
        writer.pages[1],{
            fields['sum_short_long']: str(totalShortAndLong),
            fields['l18'] : '0',
            fields['l19'] : '0'
        })
    # write "Output-beta" to pypdf-Output-beta.pdf
    with open(outputfile, "wb") as output_stream:
        writer.write(output_stream)
    forms.append('schedule D')
    return int(totalShortAndLong)


# other income - DMEI LIYDA
# 'C:\\Users\\aman\\PycharmProjects\\pdfAutoCompliter\\fields_forms\\schedule1_fields'
def schedule_1(schedulePath, scheduleFields ,reason='MATERNITY PAY' ,outputfile =output + 'schedule1'+outputEndix):

    data = configObjToArray('CALC_DATA', '.\\.editconfig')
    if not data['dmei_liyda'].isnumeric():
        print('Error in file: '+schedulePath+ ': Dmei-lyda is not recognized value')
        return 0

    if  data['dmei_liyda'].isnumeric() and int(data['dmei_liyda']) <= 0 :
        print('Dmei-Lyda is 0.')
        return 0

    dmei_lida_USD = int(float(data['dmei_liyda']) / float(data['ils_usd_rate']))

    fields = configObjToArray('FIELDS', scheduleFields)
    personal_data = configObjToArray('FILLER_DETAILS', '.\\.editconfig')

    reader = PdfReader(schedulePath)
    writer = PdfWriter()
    writer.append(reader)
    writer.update_page_form_field_values(
        writer.pages[0], {
            fields['name']: personal_data['name'] + ' ' + personal_data['family_name'],
            fields['ssn']: personal_data['ssn'],
            # fields['other_income_sum'] : ,
            fields['other_income_src']: reason,
            fields['other_income_amount']: dmei_lida_USD,
            fields['total_income']: dmei_lida_USD,
            fields['sum']: dmei_lida_USD})

    # write "Output-beta" to pypdf-Output-beta.pdf
    with open(outputfile, "wb") as output_stream:
        writer.write(output_stream)
    forms.append('schedule 1')
    return int (dmei_lida_USD)