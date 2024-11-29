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
 * Function LinkedDataset
 * 
 * @param {{dataset_name:string, dataset_row_count:number, columns:Array, columnNames_key:string}} argObject
 * * `dataset_name` imported dataest name
 * * `dataset_row_count` number of sample in dataset
 * * `columns` array of column names & column values
 * * `columnNames_key` the "column name" of "row of column names"
 * @returns {JSX.Element}
 */
export default function LinkedDataset(argObject = { dataset_name: "", dataset_row_count: 0, columns: [], columnNames_key: "" }) {
  // The `useMemo()` function will only recalculate the value of the variable when the object changes.
  let dataset_object = useMemo(() => {
    return argObject;
  }, []);
  // console.log('LinkedDataset', dataset_object);

  // Unpack
  const { dataset_name, dataset_row_count, columns, columnNames_key } = dataset_object;

  // Making table content: unpack columnNames for <TableHead/>, unpack columnValues for <TableBody/>
  const columnNames = []
  const columnValues = []
  columns.forEach((element, index) => {
    for (const key in element) {
      if (key == columnNames_key) {
        const colName = element[key]; // API JSON: "col"
        columnNames.push(
          <TableCell align="left">{colName}</TableCell>
        )
      } else {
        const colValue = element[key]; // API JSON: "func"
        columnValues.push(
          <TableCell align="left">{(colValue == "No_setting") ? "未設定" : colValue}</TableCell>
        )
      }
    }
  });

  // Return rendered elements
  return (
    <>
      <Typography variant="h4">
        資料集名稱: {dataset_name}
      </Typography>
      <Typography variant="subtitle2">
        資料筆數: {dataset_row_count}
      </Typography>

      <TableContainer component={Paper} sx={{ border: '1px solid black' }}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow sx={{ '&:last-child td, &:last-child th': { border: 1 } }}>
              <TableCell align="center">欄位名稱</TableCell>
              {columnNames}
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow sx={{ '&:last-child td, &:last-child th': { border: 1 } }}>
              <TableCell align="center">直接識別處理方式</TableCell>
              {columnValues}
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}
