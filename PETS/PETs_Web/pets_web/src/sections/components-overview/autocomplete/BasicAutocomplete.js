import { useState, useEffect } from 'react';

// material-ui
import { Autocomplete, Grid, TextField } from '@mui/material';

// project import
import MainCard from 'components/MainCard';
// import data from 'data/movies';

// ==============================|| AUTOCOMPLETE - BASIC ||============================== //

export default function BasicAutocomplete({ options, inputValue, setInputValue, setSelectedId}) {
    // console.log('inputValue in BasicAutocomplete', inputValue);
    const [value, setValue] = useState(inputValue);
    useEffect(() => {
        console.log('inputValue', inputValue);
        if(inputValue) {
            if(inputValue.length===0){
                setValue("123");
            }
            setValue(inputValue);
        } else {
            setValue("");
        }
    }, [inputValue]);

  return (
    // <MainCard title="Basic" sx={{ overflow: 'visible' }}>
    //   <Grid container spacing={2}>
        <Grid item xs={12}>
          <Autocomplete
            fullWidth
            disablePortal
            clearOnBlur={true}
            id="basic-autocomplete-label"
            key={inputValue}
            value={value}
            onChange={(event, newValue) => {
                console.log('event, newValue', event, newValue);
                setValue(newValue);
                if(newValue) {
                    setSelectedId(newValue.id);
                }
            }}
            inputVale={inputValue}
            onInputChange={(event) => {
                if(event) {
                    // console.log('event.target.value', event.target.id, event.target.outerText);
                    console.log('event.target.outerText', event.target.outerText);
                    setInputValue(event.target.outerText);
                }
            }}
            options={options}
            getOptionLabel={(option) => option.label}
            renderInput={(params) => {
                console.log('...params', params);
                // if(inputValue) {
                    return <TextField {...params} />
                // } else {
                //     return <TextField />
                // }
            }}
          />
        </Grid>
      // </Grid>
    // </MainCard>
  );
}
{/*<Grid item xs={12} lg={6}>*/}
        {/*  <Autocomplete*/}
        {/*    fullWidth*/}
        {/*    disablePortal*/}
        {/*    id="basic-autocomplete"*/}
        {/*    options={options}*/}
        {/*    renderInput={(params) => <TextField {...params} placeholder="Placeholder" />}*/}
        {/*  />*/}
        {/*</Grid>*/}