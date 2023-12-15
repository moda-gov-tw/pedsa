// import PropTypes from 'prop-types';
// import NextLink from 'next/link';

// material-ui
import {Box} from "@mui/material";

// project import
// import LogoMain from './LogoMain';
// import LogoIcon from './LogoIcon';
// import { DEFAULT_PATH } from 'config';

// ==============================|| MAIN LOGO ||============================== //

const LogoSection = ({isIcon}) => {
    console.log('isIcon', isIcon);
    return (
        <>
            {isIcon ? (
                <Box component="img" src={'/assets/images/tp-logo-small.jpg'} sx={{  width: "100%", mb: '20px' }}/>
            ) : (
                <Box component="img" src={'/assets/images/logo.png'} sx={{  width: "100%", pl: '0px', mb: '20px' }}/>
                )
            }
        </>
    );
    // <NextLink href={!to ? DEFAULT_PATH : to} passHref>
    //   <ButtonBase disableRipple sx={sx}>
    //     {isIcon ? <LogoIcon /> : <LogoMain reverse={reverse} />}
    //   </ButtonBase>
    // </NextLink>
};


export default LogoSection;
