import PropTypes from 'prop-types';
import { useEffect } from 'react';

// material-ui
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';

// third-party
import rtlPlugin from 'stylis-plugin-rtl';
import 'uuid';

// project import
import useConfig from 'hooks/useConfig';

// ==============================|| RTL LAYOUT ||============================== //

const RTLLayout = ({ children }) => {
  const { themeDirection } = useConfig();
  // const { v4: uuidv4 } = require('uuid');
  // const nonce = uuidv4().toString('base64');
  // console.log('nonce', nonce);

  useEffect(() => {
    document.dir = themeDirection;
  }, [themeDirection]);

  const cacheRtl = createCache({
    key: themeDirection === 'rtl' ? 'rtl' : 'css',
    // nonce: nonce,
    prepend: true,
    stylisPlugins: themeDirection === 'rtl' ? [rtlPlugin] : []
  });
  // console.log('cacheRtl', cacheRtl);

  return <CacheProvider value={cacheRtl}>{children}</CacheProvider>;
};

RTLLayout.propTypes = {
  children: PropTypes.node
};

export default RTLLayout;
