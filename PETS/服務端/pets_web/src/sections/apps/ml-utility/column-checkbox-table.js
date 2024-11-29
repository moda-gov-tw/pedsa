import { useEffect, useState } from 'react';

// material-ui
import {
    Checkbox,
    FormControlLabel,
    FormGroup,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';


// ==============================|| MUI TABLE WITH CHECKBOX IN HEADER||============================== //
/**
 * Function: ColumnCheckboxTable
 *
 * Child component of MLUtility
 *
 * @param {{ columns: object, data: object }} argObject
 * * `columns`: columns in the table. ex: ['c1', 'c2', 'c3']
 * * `data`: data in the table. ex: [{'c1': 1, 'c2': 1, 'c3': 2}, {'c1': 1, 'c2': 2, 'c3': 1}]
 *
 * @returns {JSX.Element}
 */
function ColumnCheckboxTable({columns, data, columnsSelected, setColumnsSelected}) {

    const handleColumnsSelected = (event) => {
        setColumnsSelected({...columnsSelected, [event.target.name]: !columnsSelected[event.target.name]});
    };
    return (
        <>
            <TableContainer component={Paper} >
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    {/*<TableCell>Column Name</TableCell>*/}
                    {columns.map((c) => (
                        <TableCell key={c} align="right">
                          <FormGroup >
                            <FormControlLabel control={<Checkbox checked={columnsSelected[c]} name={c} onChange={handleColumnsSelected} />} label={c} />
                          </FormGroup>
                        </TableCell>
                    ))}
                  </TableRow>
                </TableHead>

                <TableBody>
                  {data.map((row) => (
                    <TableRow
                      key={row.index}
                    >
                      {/*<TableCell>{row.index}</TableCell>*/}
                      {Object.keys(columns).map((id) => (
                          <TableCell align="right">{row[columns[id]]}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
        </>
    );
}

export default ColumnCheckboxTable;