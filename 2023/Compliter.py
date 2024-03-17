from pypdf import PdfReader, PdfWriter

import Schedules
import Util
from Schedules import form_1116, calcTax, f8812, capitalGain, schedule_1
from Util import configObjToArray


def pdf (option , confPath = '.editconfig'):

    c ={}
    a = Util.configObjToArray(option , confPath) # a = {sch , dsdssaas}
    for i in a:
        c[i] = Util.extractArrFromStringConfigFile(a[i])

    dirs = configObjToArray('DIRS', '.editconfig')
    pdfDir = dirs['pdfs'] + '\\'
    fieldDir = dirs['fields_forms'] + '\\'
    for i in c:
        if c[i] is None:
            continue
        c[i]['name'] = pdfDir + c[i]['name']
        c[i]['fieldsFile'] =fieldDir +  c[i]['fieldsFile']
    return c



pdfs = pdf('PDF_FORMS')

def reader():

    Schedules.createOutputFolder()
    calc   = configObjToArray('CALC_DATA', '.editconfig')
    fields = configObjToArray('FIELDS', pdfs['1040']['fieldsFile'])
    filler = configObjToArray('FILLER_DETAILS', '.editconfig')
    dependets = configObjToArray('DEPENDENCE', '.editconfig')
    dividends = configObjToArray('DIVIDENDS', '.editconfig')
    short_term= configObjToArray('SHORT_TERM', '.editconfig')
    long_term= configObjToArray('LONG_TERM', '.editconfig')

    dependetsArr = {}
    for i in dependets:
        dependetsArr[i] = Util.extractArrFromStringConfigFile(dependets[i])


    salaryInUSD = int(float(calc['salary_in_ils']) / float(calc['ils_usd_rate']))


    #lines in 1040 2023

    l1a = salaryInUSD
    l1h = salaryInUSD
    l3a = dividends['qualified_dividend']
    l3b = int(dividends['ordinary_dividend'])
    l7 = int(capitalGain(pdfs['scheduled']['name'] ,pdfs['scheduled']['fieldsFile']))
    l8 = int(schedule_1( pdfs['schedule1']['name'] ,pdfs['schedule1']['fieldsFile']))
    l9 = int(l1a)+int(l3b)+int(l7)+int(l8)
    l10 = 0 #adjestmnets
    l11 = l9-l10
    l12= int(calc['standard_deduction'])
    l14=l12
    l15=l11-l14

    l16 = calcTax(l15)
    l17 = 0
    l18 = l16+l17
    # this line is bifore l19, due i need l20 to b in l19
    l20 = form_1116 (pdfs['form_1116']['name'] , pdfs['form_1116']['fieldsFile'],pdfs['schedule3']['name'] ,pdfs['schedule3']['fieldsFile'],
                   l15, l16 )
    f8812_re = f8812(pdfs['form_8812']['name'] ,pdfs['form_8812']['fieldsFile'], l1a , l11,l18, l20  , len(dependets))#Suppose to b after s3
    l19 = f8812_re['l19']
    l21 = l19 + l20
    l22 = l18 - l21
    if l22 < 0:
        l22=0
    l23=0
    l24=l22+l23

    l25a = 0
    l25b = 0
    l25c = 0
    l25d = 0
    l26 =  0
    l27 =  0
    l28 = f8812_re['l28']
    l29= 0
    #l30  - reserved for future use
    l31_s3l15= 0
    l32= l27+ l28+ l29+ l31_s3l15
    l33 = l25d+ l26+ l32
    l34 = 0
    if l33 > l24:
        l34=l33-l24
    l35 = l34 #amount to be refunded
    l36 = 0
    l37 = l24 - l33
    if l37 < 0:
        l37 = 0
    l38 = 0

    reader = PdfReader(pdfs['1040']['name'])
    writer = PdfWriter()

    writer.append(reader)


    writer.update_page_form_field_values(
            writer.pages[0] , {
                                fields['start_date']:'1.1.23',
                                fields['end_date']: '12.31',
                                fields['end_date_year']: '23',
                                fields['first_name']:filler['name'],
                               fields['family_name']:filler['family_name'],
                               fields['personal_ssn']:filler['ssn'],
                               fields['apartment']: filler['apt'],
                               fields['address']:filler['address'],
                               fields['city']:filler['city'],
                               fields['country1']:filler['country'],
                               fields['zip1']:filler['zip'],
                               fields['country2']:filler['country'],
                               fields['country3']:filler['country'],
                               fields['zip2']:filler['zip'],

                                fields['salary']: str(l1a),
                                fields['sum_salary']: str(l1h),
                                fields['qualified_dividends']:str(l3a),
                                fields['ordinary_dividends'] : str(l3b),
                                fields['capital_gain']:str(l7),
                                fields['total_income']:str (l9),
                                fields['total_adjusted']:str(l10),
                                fields['total_income_adjusted']:str(l11),
                                fields['standard_deduction']:str(l12),
                                fields['total_dedction']:str(l14),
                                fields['l15_taxable_income']:str(l15)
                         })

    writer.update_page_form_field_values(
                        writer.pages[1], {
                                fields['l16_tax']:str(l16),
                                fields['l17_amount_s2l3-0']:str(l17),
                                fields['l18_add_l16_l17']:str(l18),
                                fields['l19_childtaxcredit_8812l19-0']:str(l19),
                                fields['l20_amount_s3l8-0']:str(l20),
                                fields['l21_add_l20_l19']:str(l21),
                                fields['l22_l18_sub_l21']:str(l22),
                                fields['l23_othertaxes_s2l21-0']:str(l23),
                                fields['l24_add_22_23']:str(l24),
                                fields['l25a_federalincome_w2-0']:str(l25a),
                                fields['l25b_federalincome_1099-0']:str(l25b),
                                fields['l25c_other_forms-0']:str(l25c),
                                fields['l25d_total_a-c-0']:str(l25d),
                                fields['l26_estimated_2021_return_overpaid-0']:str(l26),
                                fields['l27_eic-0']:str(l27),
                                fields['l28_aditional_childtaxcredit_8812l27']:str(l28),
                                fields['l29_american_oppornunity-0']:str(l29),
                                fields['l31_amount_s3l15-0']:str(l31_s3l15),
                                fields['l32_add_ll27_l28_l29_l31-l28']:str(l32),
                                fields['l33_totalpayments_add_l25b_l26_l32']:str(l33),
                                fields['l34_l33_isbigger_l24_sub_l33_l24']:str(l34),
                                fields['l35a_amount_to_refound']:str(l35),
                                fields['l35b_routing']:filler['rout'] ,
                                fields['l35d_account']:filler['account'],
                                fields['l36_sum_to_apply_next_year-0']:str(l36),
                                fields['l37_l24_sub_l33-0']:str(l37),
                                fields['l38_estimated_tax_penalty-0']:str(l38),
                                fields['occupation']:filler['occupation'],
                                fields['phone']:filler['phone'],
                                fields['email']:filler['email'],
            } )

    outdir = configObjToArray('DIRS', '.editconfig')['output_folder'] + '\\'
    output = outdir + configObjToArray('OTHER_FORMS', '.editconfig')['summarizedfilename']


    with open(output, "w") as declarations:
        declarations.write('\n\n===========     ILS/DOLLAR RATE   ============\n\n')
        declarations.write('1 USD = ' + calc['ils_usd_rate'].__str__() + ' ILS')

    j = 1
    for i in dependetsArr:
        if j <= 4:
            writer.update_page_form_field_values(writer.pages[0], {
                fields['dep_' + str(j) + '_name']: dependetsArr[i]['name'],
                fields['dep_' + str(j) + '_ssn']: dependetsArr[i]['ssn'],
                fields['dep_' + str(j) + '_gen']: dependetsArr[i]['rel']
            })
        else:
            with open(output, "a") as declarations:
                if j == 5:
                    declarations.write('\n===========     DEPENDENCIES    ===================\n')
                declarations.write(str(j) + ' > ' + 'Name:' +dependetsArr[i]['name']+
                     '  SSN: ' +dependetsArr[i]['ssn']+ '  Relation: ' +dependetsArr[i]['rel']+ '  Qualifies for Child tax credit [V]\n')

        j+=1
    declarations.close()

    with open(output, "a") as declarations:
        declarations.write('===========     ADDED FORMS     =================\n')
        for i in Schedules.forms:
            declarations.write(str(Schedules.forms.index(i)+1)+' > '+i+'\n')

    Util.writePdfFile(output)

    with open(outdir +'1040.pdf', "wb") as output_stream:
        writer.write(output_stream)

    print('Mission complete. see your files at : ' + outdir +'\nSee you next year!  ;)')
reader()
# print(dirs['fields_forms'] +'\\'+pdfs['1040']['fieldsFile'])
# print( dirs['fields_forms'] +'\\'+pdfs['1040']['fieldsFile'])