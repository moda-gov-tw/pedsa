import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

// ==============================|| DOWNLOAD COMPONENT AS PDF FILE ||============================== //
// 先把元件做成圖片
// 把圖片放到pdf上，儲存pdf檔案

/**
 * Function: downloadPdfDocument
 *
 * Download react component as pdf file.
 *
 * @param {string} rootElementId
 * - Element id to download as pdf.
 * @param {string} downloadFileName
 * - Filename for downloaded pdf.
 */
export async function downloadPdfDocument( rootElementId ,downloadFileName ) {
    const input = document.getElementById(rootElementId);
    // 元件寬度
    const originWidth = input.offsetWidth;
    const scale = 2;
    const width = originWidth + 32;
    // console.log('width', input.offsetWidth);
    // 直式pdf檔案長寬比為1.414:1
    const PDF_WIDTH = width * scale;
    const PDF_HEIGHT = width * 1.414 * scale;

    html2canvas(input)
        .then((canvas) => {
            // 下載圖片
            // var a = document.createElement('a');
            // a.href = canvas.toDataURL("image/jpeg").replace("image/jpeg", "image/octet-stream");
            // a.download = 'test.jpg';
            // a.click();
            const contentWidth = canvas.width;
            const contentHeight = canvas.height;

            // 一頁pdf可以畫出來的圖片高度
            const pageHeight = contentWidth / PDF_WIDTH * PDF_HEIGHT;

            // canvas圖片畫出來的尺寸
            const imgWidth = PDF_WIDTH;
            const imgHeight = PDF_WIDTH / contentWidth * contentHeight;

            //剩下圖片的高度
            let leftHeight = contentHeight;

            let position = 0;

            // jsPDF(直向/橫向, 單位, [自訂規格])
            const pdf = new jsPDF('p', 'px', [PDF_WIDTH, PDF_HEIGHT]);

            // 不到一頁
            if (leftHeight < pageHeight) {
                pdf.addImage(canvas, 'PNG', 0, 0, imgWidth, imgHeight);
            } else {
                // 多頁
                while (leftHeight > 0) {
                  pdf.addImage(canvas, 'PNG', 0, position, imgWidth, imgHeight)
                  leftHeight -= pageHeight;
                  position -= PDF_HEIGHT;

                  if (leftHeight > 0) {
                    pdf.addPage();
                  }
                }
            }
            pdf.save(`${downloadFileName}.pdf`);
        });
}