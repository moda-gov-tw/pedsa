import React, { useReducer } from 'react';
// material-ui
import { Autocomplete, Checkbox, TextField, Chip } from '@mui/material';

// project import
import data from 'data/movies';

// ==============================|| AUTOCOMPLETE - CHECKBOXES ||============================== //
export default function CheckboxesAutocomplete({ options = data, placeholderText = "Checkboxes", getselectedOptions = () => {} }) {

    const initialState = { selectedOptions: [] };

    function reducer(state, action) {
      switch (action.type) {
        case "SET_SELECTED_OPTIONS":
              return {selectedOptions: action.payload.options};

        case "REMOVE_OPTION":{
              // console.log('remove', action.payload.label);
              // console.log('rm', state.selectedOptions.filter(
              //   (option) => option.label !== action.payload.label
              // ));
              let selectedOptionsTemp = state.selectedOptions.filter(
                  (option) => option.label !== action.payload.label
              );
              let temp = [];
              if (selectedOptionsTemp.length > 0) {
                  selectedOptionsTemp.map((selectedOption) => {
                      temp.push(selectedOption.label);
                  });
              }
              getselectedOptions(temp);
              return {
                  selectedOptions: selectedOptionsTemp
                  // selectedOptions: state.selectedOptions.filter(
                  //   (option) => option.label !== action.payload.label
                  // )
              };
        }

        case "CLOSE": {
            // let keepState = state.selectedOptions;
            let temp = [];
            if (state.selectedOptions.length > 0) {
                state.selectedOptions.map((selectedOption) => {
                    temp.push(selectedOption.label);
                });
            }
            getselectedOptions(temp);
            return {selectedOptions: state.selectedOptions};
        }
        default:
          throw new Error();
      }
    }
    const [state, dispatch] = useReducer(reducer, initialState);

    const handleChange = (event, values) => {
      dispatch({ type: "SET_SELECTED_OPTIONS", payload: { options: values } });
    };

    const removeOption = (label) => {
      dispatch({ type: "REMOVE_OPTION", payload: { label: label } });
    };

    const handleClose = () => {
      dispatch({ type: "CLOSE" } );
    };

    return (
    <>
      <Autocomplete
        multiple
        id="checkboxes-tags-demo"
        options={options}
        disableCloseOnSelect
        // filterSelectedOptions={true}
        getOptionLabel={(option) => option.label}
        value={state.selectedOptions}
        renderTags={(values) =>
          values.map((value) => (
            <Chip
              key={value.id}
              label={value.label}
              onDelete={() => {
                removeOption(value.label);
              }}
            />
          ))
        }
        isOptionEqualToValue={(option, value) => option.label === value.label}
        // renderOption={(props, option, { selected }) => (
        renderOption={(props, option) => (
          <li {...props}>
            <Checkbox style={{ marginRight: 8 }} checked={!!state.selectedOptions.find((o) => o.label === option.label)} name={option.label} />
            {option.label}
          </li>
        )}
        onChange={handleChange}
        renderInput={(params) => <TextField {...params} placeholder={placeholderText} />}
        onClose={handleClose}
        // onClose={() => handleClose(event, state.selectedOptions)}
        sx={{
          '& .MuiOutlinedInput-root': {
            p: 1
          },
          '& .MuiAutocomplete-tag': {
            bgcolor: 'primary.lighter',
            border: '1px solid',
            borderColor: 'primary.light',
            '& .MuiSvgIcon-root': {
              color: 'primary.main',
              '&:hover': {
                color: 'primary.dark'
              }
            }
          }
        }}
      />
      {/*<pre>{JSON.stringify(state, null, 2)}</pre>*/}
    </>
  );
}
