// next
import NextAuth from 'next-auth';
import Auth0Provider from 'next-auth/providers/auth0';
import CredentialsProvider from 'next-auth/providers/credentials';
import CognitoProvider from 'next-auth/providers/cognito';
import GoogleProvider from 'next-auth/providers/google';

// third-party
import axios from 'axios';

export let users = [];

export default NextAuth({
  secret: process.env.NEXTAUTH_SECRET_KEY,
  providers: [
    Auth0Provider({
      name: 'Auth0',
      clientId: process.env.AUTH0_CLIENT_ID,
      clientSecret: process.env.AUTH0_CLIENT_SECRET,
      issuer: `https://${process.env.AUTH0_DOMAIN}`
    }),
    CognitoProvider({
      name: 'Cognito',
      clientId: process.env.COGNITO_CLIENT_ID,
      clientSecret: process.env.COGNITO_CLIENT_SECRET,
      issuer: `https://cognito-idp.${process.env.COGNITO_REGION}.amazonaws.com/${process.env.COGNITO_POOL_ID}`
    }),
    GoogleProvider({
      name: 'Google',
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code'
        }
      }
    }),
    // functionality provided for credentials based authentication is intentionally limited to discourage use of passwords due to the
    // inherent security risks associated with them and the additional complexity associated with supporting usernames and passwords.
    // We recommend to ignore credential based auth unless its super necessary
    // Ref: https://next-auth.js.org/providers/credentials
    // https://github.com/nextauthjs/next-auth/issues/3562
    CredentialsProvider({
      id: 'login',
      name: 'Login',
      credentials: {
        account: { label: 'Account', type: 'account', placeholder: '' },
        password: { label: 'Password', type: 'password', placeholder: '' }
      },
      async authorize(credentials) {
        try {
          const user = await axios.post(`${process.env.NEXTAUTH_URL}/api/auth/login`, {
            account: credentials?.account,
            password: credentials?.password,
          });

          if (user) {
            return user.data;
          }
        } catch (e) {
          const errorMessage = e?.response.data.message;
          throw new Error(errorMessage);
        }
      }
    }),
    // functionality provided for credentials based authentication is intentionally limited to discourage use of passwords due to the
    // inherent security risks associated with them and the additional complexity associated with supporting usernames and passwords.
    // We recommend to ignore credential based auth unless its super necessary
    // Ref: https://next-auth.js.org/providers/credentials
    // https://github.com/nextauthjs/next-auth/issues/3562
    CredentialsProvider({
      id: 'register',
      name: 'Register',
      credentials: {
        name: { label: 'Name', type: 'text', placeholder: 'Enter Name' },
        email: { label: 'Email', type: 'email', placeholder: 'Enter Email' },
        password: { label: 'Password', type: 'password', placeholder: 'Enter Password' }
      },
      async authorize(credentials) {
        try {
          const user = await axios.post(`${process.env.NEXTAUTH_URL}/api/auth/register`, {
            name: credentials?.name,
            password: credentials?.password,
            email: credentials?.email
          });

          if (user) {
            users.push(user.data);
            return user.data;
          }
        } catch (e) {
          const errorMessage = e?.response.data.message;
          throw new Error(errorMessage);
        }
      }
    })
  ],
  callbacks: {
    jwt: async ({ token, user, account }) => {
      if (user) {
        token.id = user.obj.member_id;
        token.provider = account?.provider;
        token.account = user.obj.account_name;
        token.loginUserToken = user.obj.token;
      }
      return token;
    },
    session: async ({ session, token }) => {
      if (token) {
        session.id = token.id;
        session.provider = token.provider;
        session.tocken = token;
      }
      return session;
    }
  },
  session: {
    strategy: 'jwt',
    maxAge: Number(process.env.JWT_TIMEOUT)
  },
  jwt: {
    secret: process.env.JWT_SECRET
  },
  pages: {
    signIn: '/login',
    newUser: '/register'
  }
});
