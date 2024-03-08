from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    get_orders()
    read_table()
    archive_receipts()
    
    
def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
    csv = Tables()
    table = csv.read_table_from_csv("orders.csv", header=True)
    return table

def read_table():
    orders = get_orders()
    for order in orders:
        on = order['Order number']
        close_annoying_modal()
        fill_the_form(order)
        embed_screenshot_to_receipt(screenshot_robot(on), store_receipt_as_pdf(on))
        next_robot()

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")
    
def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", order['Head'])
    page.click("#id-body-{}".format(str(order['Body'])))
    page.fill("//input[@type='number']", order['Legs'])
    page.fill("#address", order['Address'])
    page.click("#order")
    flag = page.is_visible("//div[@class='alert alert-danger']")
    while flag:
        page.click("#order")
        flag = page.is_visible("//div[@class='alert alert-danger']")
             
def store_receipt_as_pdf(order_number):
    pdf = PDF()
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(receipt, "output/receipts/{}.pdf".format(str(order_number)))
    pdfPath = "output/receipts/{}.pdf".format(str(order_number))
    return pdfPath
    
def screenshot_robot(order_number):
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path="output/img/{}.png".format(str(order_number)))
    img = "output/img/{}.png".format(str(order_number))
    return img
    
def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file)
    
def next_robot():
    page = browser.page()
    page.click("#order-another")
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip(folder="output/receipts", archive_name="output/receipts.zip")