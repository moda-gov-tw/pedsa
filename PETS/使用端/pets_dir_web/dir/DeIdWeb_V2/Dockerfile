#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

#FROM mcr.microsoft.com/dotnet/aspnet:3.1 AS base
FROM mcr.microsoft.com/dotnet/core/sdk:3.1 AS build-env
WORKDIR /app
#RUN apt-get install -y dotnet-sdk-2.1
RUN echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN apt-get update && apt-get install -y libgdiplus
RUN apt-get update && apt-get install -y openssh-server
RUN apt-get install -y fonts-wqy-microhei ttf-wqy-microhei fonts-wqy-zenhei ttf-wqy-zenhei

#
## copy csproj and restore as distinct layers
COPY *.csproj ./
RUN dotnet restore
#ADD server.pfx /app/
## copy everything else and build app
#COPY . ./
#RUN dotnet publish -c Release -o out
#
#
## build runtime image
#FROM mcr.microsoft.com/dotnet/core/aspnet:3.1
#WORKDIR /app
#COPY --from=build-env /app/out .
#
## set environment variables for HTTPS
#ENV ASPNETCORE_URLS=https://+:443 \
    #ASPNETCORE_HTTPS_PORT=443
#
#ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]


COPY . ./
RUN dotnet publish -c Release -o out


#FROM mcr.microsoft.com/dotnet/core/aspnet:3.1 AS final 
ENV ASPNETCORE_URLS=https://+:11050
WORKDIR /app
EXPOSE 11050/tcp
#COPY --from=build /app/out .
#ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]
entrypoint ["dotnet","run","--server.urls","https://localhost:11050"]

##FROM mcr.microsoft.com/dotnet/core/aspnet:3.1 AS final 
#ENV ASPNETCORE_URLS=https://+:11000
#WORKDIR /app
#EXPOSE 11000/tcp
##COPY --from=build /app/out .
##ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]
#entrypoint ["dotnet","run","--server.urls","https://localhost:443"]
##FROM mcr.microsoft.com/dotnet/sdk:3.1 AS build
##WORKDIR /src
##COPY ["../DeIdWeb_V2/DeIdWeb_V2.csproj", "DeIdWeb_V2/"]
##RUN dotnet restore "DeIdWeb_V2/DeIdWeb_V2.csproj"
##COPY . .
##WORKDIR "/src/DeIdWeb_V2"
##RUN dotnet build "DeIdWeb_V2.csproj" -c Release -o /app/build
##
##FROM build AS publish
##RUN dotnet publish "DeIdWeb_V2.csproj" -c Release -o /app/publish
##
##FROM base AS final
##WORKDIR /app
##COPY --from=publish /app/publish .
###ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]
##entrypoint ["dotnet","run","--server.urls","http://localhost:11000"]
##
#