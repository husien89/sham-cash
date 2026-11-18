from fpdf import FPDF
from datetime import datetime

class DekontPDF(FPDF):
    def header(self):
        # --- HEADER (الشعار واسم البنك) ---
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(0, 51, 102) # أزرق غامق
        self.cell(0, 15, 'SHAM CASH BANK', 0, 1, 'R')
        
        # --- INFO SECTION (الاسم والتاريخ) ---
        self.set_font('Helvetica', '', 12)
        self.set_text_color(50, 50, 50)
        self.cell(0, 5, 'Account Statements / كشف حساب', 0, 1, 'L')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, title, 0, 1, 'L')

    def info_box(self, label, value):
        self.set_font('Helvetica', 'B', 10)
        self.cell(100, 6, label, 0, 0, 'L')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 6, value, 0, 1, 'L')

    def print_table(self, header, data, col_widths):
        # Print Header
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        
        for i in range(len(header)):
            self.cell(col_widths[i], 7, header[i], 1, 0, 'C', True)
        self.ln()

        # Print Data
        self.set_font('Helvetica', '', 9)
        fill = False
        for row in data:
            self.set_fill_color(255, 255, 255)
            if fill: self.set_fill_color(245, 245, 245) # تلوين الصفوف بالتناوب
            
            for i in range(len(header)):
                self.cell(col_widths[i], 7, str(row[i]), 1, 0, 'C', True)
            self.ln()
            fill = not fill

# --- دالة التوليد الرئيسية ---
def generate_dekont(user_data, transactions, outfile="dekont.pdf"):
    pdf = DekontPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 1. بيانات المستخدم (العميل)
    pdf.section_title('CLIENT INFORMATION')
    pdf.info_box('Name:', user_data['name'])
    pdf.info_box('Account No:', user_data['account'])
    pdf.info_box('Currency:', user_data['currency'])
    pdf.ln(5)

    # 2. بيانات الحساب (الحسابات المربوطة)
    pdf.section_title('ACCOUNT DETAILS')
    pdf.info_box('Branch:', 'Main Branch')
    pdf.info_box('Account Type:', 'Savings Account')
    pdf.info_box('Status:', 'Active')
    pdf.ln(5)

    # 3. جدول المعاملات
    pdf.section_title('TRANSACTION HISTORY')
    header = ['Date', 'Description', 'In', 'Out', 'Balance']
    # تحويل البيانات للتنسيق المطلوب
    table_data = []
    for tx in transactions:
        table_data.append([
            tx['date'], 
            tx['desc'], 
            f"{tx['in']:.2f}" if tx['in'] > 0 else "", 
            f"{tx['out']:.2f}" if tx['out'] > 0 else "", 
            f"{tx['bal']:.2f}"
        ])
    
    # عرض الجدول
    pdf.print_table(header, table_data, [30, 80, 30, 30, 30])

    pdf.ln(10)
    
    # 4. التذييل
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 10, 'This statement is computer generated.', 0, 1, 'C')

    pdf.output(outfile)
    return outfile

# --- مثال للاستخدام ---
if __name__ == "__main__":
    # بيانات تجريبية
    user = {
        'name': 'ABDULLAH AHMED',
        'account': 'SH-9988776655',
        'currency': 'SAR / SHAM'
    }
    
    # بيانات المعاملات (محاكاة لما يأتي من قاعدة البيانات)
    txs = [
        {'date': '2023-10-01', 'desc': 'Opening Balance', 'in': 0, 'out': 0, 'bal': 5000.00},
        {'date': '2023-10-05', 'desc': 'Transfer to User B', 'in': 0, 'out': 500.00, 'bal': 4500.00},
        {'date': '2023-10-10', 'desc': 'Deposit