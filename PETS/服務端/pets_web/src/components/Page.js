import PropTypes from 'prop-types';
import { forwardRef } from 'react';

// next
import Head from 'next/head';
// import { headers } from 'next/headers';

// material-ui
import { Box } from '@mui/material';

// ==============================|| Page - SET TITLE & META TAGS ||============================== //

const Page = forwardRef(({ children, title = '', meta, ...other }, ref) => {
    // const nonce = headers().get('x-nonce');nonce={nonce}nonce={nonce}
    return (
        <>
            <Head >
                <title>{`${title} | Mantis React Admin`}</title>
                {meta}
            </Head>

            <Box ref={ref}  {...other} >
                {children}
            </Box>
        </>
    );

});

Page.propTypes = {
  title: PropTypes.string,
  meta: PropTypes.node,
  children: PropTypes.node
};

export default Page;
