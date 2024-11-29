This is a starter template for [Learn Next.js](https://nextjs.org/learn).

* Start Pets_web service (next.js server) with docker

    * Step 1: Build image
        
        ```bash 
        $ bash build.sh
        # build.sh will build new image and remove the old same name image 
        ```
        or
        ```bash 
        $ docker-compose build
        # or below command (depends on your docker-compose version or installation method)
        # $ docker compose build
        ```
        It may take 10 to 20 minutes. Please wait patiently. 
          
        The success message will be displayed after the build is finished.
        ```
        Successfully tagged petsservice/web:1.0
        ```
        (P.S.: default `<IMAGE-ID>:<TAG>` should be `petsservice/web:1.0`)

    * Step 2: Start the container

        ```bash 
        $ docker-compose up
        # or below command (depends on your docker-compose version or installation method)
        # $ docker compose up
        ```
        The success message will be displayed after the build is finished.
        ```
        Creating pets-web ... done
        ```
        or
        ```
        ✔ Container pets-web Started
        ```

    * Step 3: Open brower and connect to url
        
        Dev mode
        ```
        http://<server-ip>:8081
        ```
        Deploy mode

        [!] **You need to** first uncomment the `#RUN yarn build` and `#CMD ["yarn", "start"]` in the Dockerfile, and then delete the `CMD ["yarn", "dev"]`. Then go back to step 1.
        ```
        http://<server-ip>:3000
        ```

* To stop the container:
    ```bash
    $ docker container stop <CONTAINER-ID>
    ```
    or
    ```bash
    $ docker-compose down
    # or below command (depends on your docker-compose version or installation method)
    # $ docker compose down
    ```