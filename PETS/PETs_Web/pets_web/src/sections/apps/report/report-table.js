// material-ui
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from "@mui/material";

// project import
import {ganColValDic1} from "../../../data/gan-report-columns";


// ==============================|| PROJECT - REPORT TABLE||============================== //
/**
 * Function: ReportTable
 *
 * Child component of GanReport, KReport
 *
 * @param {{ columns: object, rows: object, colDic: object }} argObject
 * * `columns`: value of columns.
 * * `rows`: value of rows.
 * * `colDic`: mapping of english and chinese column name.
 *
 * @returns {JSX.Element}
 */
const ReportTable = ({ columns, rows, colDic }) => {

  function preprocessColVal(colVal) {
    // console.log('colVal', colVal);
    let colValView = '';
    // gan colVal type 1
    // {
    //   "min": 1,
    //   "max": 2,
    //   "mean": 1.498,
    //   "median": 1,
    //   "std": 0.5002461856388775
    // }

    if(Object.keys(colVal).includes('min')) {
      Object.keys(colVal).map((k) => {
        colValView = colValView + ganColValDic1[k] + ': ' + String(colVal[k]) + '\n';
      });
    }
    // gan colVal type 2
    // [
    //   {
    //     "col_value": "rGRiS03qGDgf87T7dSllTg==",
    //     "col_count": 388
    //   },
    //   {
    //     "col_value": "B+EArLKXQPAQT3LxnI3LjA==",
    //     "col_count": 238
    //   }
    // ]
    if(colVal[0] && Object.keys(colVal[0]).includes('col_value')) {
      colVal.map((cv) => {
        colValView = colValView + cv['col_value']+': '+String(cv['col_count'])+"筆"+" \n ";
      });
    }
    console.log('colValView', colValView);
    return colValView;
  }

  // console.log('colDic', colDic);
  return (
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              {
                columns.map((col) => (
                  <TableCell align="left">{colDic[col]}</TableCell>
                ))
              }
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) =>
              <TableRow>
                {
                  columns.map((col) => (
                      (typeof row[col] === 'object') ?
                          (<TableCell sx={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }} align="left">{preprocessColVal(row[col])}</TableCell>) :
                          (<TableCell align="left">{row[col]}</TableCell>)
                  ))
                }
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
  )
}

export default ReportTable;