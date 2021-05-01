# Project3-covid-explorer
Exploring different ML algorithm and Solidity using COVID dataset
## Background
New startup has decided to run through covid explorer program in order to help one of the health institue to perform data analysis functions. Though there are huge number of freely available covid dashboard in the internet but company decided to create inhouse capability to develop own dashboard using different machine learning algorithm and solidity.  This program will help company to show current covid trend of selected country, using linear regression algorithm predict the covid cases for selected country. Not only that it also compares two different countries data and show the trend between two different countries. Company also introduced "BlockVax" as a smart contract which interacts with the ethereum network to allow users to register a profile for themselves or others, generating a unique patient ID number and storing the profile data in a profile struct as part of a mapping. Their profile registration will require their address as well as a photo ID, which will be uploaded to [pinata](https://pinata.cloud/) and stored via an IPFS hash.

In order to launch this prgoram , company need to covid historical data which will be available and downloaded from the world health website.

This Program will run in four parts:
1. Data cleaning and data analysis Part
2. Ceating Dashboard using Python code and machine algorithm to plot different graphs using streamlit
3. Chatboat to communnnicate with the Public for covid related queries.
4. Solidity patient contract to verify whether patient has been vaccinated or not.

<details>
<summary>Creating a Project</summary>
<p>detail informaion about project and participant</p>
           
</details>
<details>

<summary>How we build it</summary>
<p>

### Team Members

* Purvi Doshi

* Antonio Aguilar

* Paulina Filippidis

* Harrison Marcus Clark

* Khushboo Bhatnagar

### Development Instruction

* pip install streamlit
* pip install altair

### Technology Used

* Python
* Streamlit
* Altair to display graph using streamlit
* Solidity
* Chatboat

</p>
</details>

<details>
<summary>Deploying the Project</summary>
<p>
1. Before deploy your app to Heroku, you need to initialize a local Git repository and commit your application code to it. The following example demonstrates initializing a Git repository for an app that lives in the finalapp directory:
           $cd covid-explorer
           $ git init
           $ git add.
</p>
 </details>
 <details>
           
  
  
#### Project Images

<summary>Streamlit Interatice webapp</summary>
 <p>
         
#### First Web Page   
![img](Images/first_page1.PNG)     

#### Second Web Page
![img](Images/second_page.PNG)

#### Third Web Page
![img](Images/third_page.PNG)

#### Fourth Web Page
![img](Images/fourth_page.PNG)

</p>
</details>
<details>
<summary>Solidity Example-BlockVax</summary>
<p>
            
 Image1            | Image2        | Image 3                         
  -----------------------|----------------------------|-----------------------
  ![img](Images/image1.png)      | ![img](Images/image2.png) | ![img](Images/image3.png)
 
</p>
</details>

#### Data Source and Resource

<details>
<summary>Data Source</summary>
<p>
1. https://github.com/owid/covid-19-data <br>
2. https://ourworldindata.org/covid-vaccinations
</p>
</details>
<details>
<summary>References</summary>
           <p>
 1. https://discuss.streamlit.io/ <br>
 2. https://streamlit.io/gallery?type=apps&category=geography-society<br>
 3. https://www.youtube.com/watch?v=k-d27B5hnqc
                     </p>

</details>

