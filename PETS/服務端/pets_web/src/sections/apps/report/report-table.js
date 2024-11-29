import { useState } from 'react';

// material-ui
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow } from '@mui/material';

// project import
import { ganColValDic1 } from '../../../data/gan-report-columns';

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
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(event.target.value);
    setPage(0);
  };

  function customLabelDisplayedRows({ from, to, count }) {
    return `第${from}–${to}筆 ${count !== -1 ? `共${count}筆` : `超過${to}筆`}`;
  }

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

    if (Object.keys(colVal).includes('min')) {
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
    if (colVal[0] && Object.keys(colVal[0]).includes('col_value')) {
      colVal.map((cv) => {
        colValView = colValView + cv['col_value'] + ': ' + String(cv['col_count']) + '筆' + ' \n ';
      });
    }
    console.log('colValView', colValView);
    return colValView;
  }

  // console.log('colDic', colDic);
  return (
    <>
      <TableContainer component={'div'}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell align="left">{colDic[col]}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => (
              <TableRow>
                {columns.map((col) =>
                  typeof row[col] === 'object' ? (
                    <TableCell sx={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }} align="left">
                      {preprocessColVal(row[col])}
                    </TableCell>
                  ) : (
                    <TableCell align="left">{row[col]}</TableCell>
                  )
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        sx={{ '.MuiTablePagination-toolbar': { width: '80%' /* , backgroundColor: '#226cea' */ } }}
        labelRowsPerPage="每頁顯示筆數"
        rowsPerPageOptions={[10, 20, 50, 100]}
        labelDisplayedRows={customLabelDisplayedRows}
        component={'div'}
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        showFirstButton
        showLastButton
      />
    </>
  );
};

export default ReportTable;
