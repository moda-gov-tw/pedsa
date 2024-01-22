import * as React from 'react';
import { useMemo } from 'react';

// material-ui
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Grid,
  Divider,
  Stack
} from '@mui/material'


/**
 * Function MultiRowTable
 * 
 * @param {Array[Object]} objectRows
 * Every object in this list indicate one piece data.
 * * columns: key is the column name, value is column value.
 * @returns {JSX.Element}
 */
export default function MultiRowTable({ objectRows, tableMinWidth = 650 }) {
  const ColumnNames = () => {
    const colNameList = [];
    // const rowHead = (<TableCell align="left" style={{ whiteSpace: 'pre-line' }}>欄位名稱</TableCell>);
    const rowTails = Object.keys(objectRows[0]).map(colName => (<TableCell align="left">{colName}</TableCell>));
    return (
      <TableRow sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
        {/* {colNameList.concat(rowHead).concat(rowTails)} */}
        {colNameList.concat(rowTails)}
      </TableRow>
    );
  }

  const ColumnValueRows = () => {
    const colValueRows = objectRows.map((objElement, index) => (
      <TableRow sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
        {/* <TableCell align="left">列名稱{index}</TableCell> */}
        {Object.entries(objElement).map(([key, colValue]) => (
          <TableCell align="left">{colValue}</TableCell>
        ))}
      </TableRow>
    ));
    return colValueRows;
  };

  // Return rendered elements
  return (
    <>
      <TableContainer component={Paper} sx={{ border: '1px solid black' }}>
        <Table sx={{ minWidth: tableMinWidth }} aria-label="simple table">
          <TableHead>
            <ColumnNames />
          </TableHead>
          <TableBody>
            <ColumnValueRows />
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}