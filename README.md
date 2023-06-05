<h1 align="center">
📖 Recovery | 42 Cybersecurity Bootcamp
</h1>

<p align="center">
	<b><i>Gathering information from the windows platform</i></b><br>
</p>

<p align="center">
	<img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/Falitomal/recovery?color=lightblue" />
	<img alt="Code language count" src="https://img.shields.io/github/languages/count/Falitomal/recovery?color=yellow" />
	<img alt="GitHub top language" src="https://img.shields.io/github/languages/top/Falitomal/recovery?color=blue" />
	<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Falitomal/recovery?color=green" />
</p>


##  ⚠️ Summary
```
The collection of evidence is a fundamental part of conducting a forensic examination. Having clear and organized information is something that can facilitate the work of the
forensic. The objective of this project is to create a program that, given a range of dates, is capable of extracting various information from a Windows system such as user activity, open programs, browsing history, different information about the user, open programs, browsing history, and other data.
activity, open programs, browsing history, different information from the Windows registry... in such a
Windows registry... in that time range.
```


## ✏️ Mandatory
```

A program should be created that, given a time range, can extract information of interest to forensics, for example:
- Log branch change dates (CurrentVersionRun).
- Recent files
- Installed programs
- Open programs
- Browsing history
- Connected devices
- Log events
If a time range is not provided, it could take a default value, for example,
the last 24 hours, the last week or the last month.

```

## ✏️ Bonus
```
You can enhance your project with the following features:
Although the collected information can be displayed per screen in an orderly manner
in different sections, you can optionally implement the following functionalities:
- Create a graphical timeline showing all evidence organized in time and by categories.
in time and by categories.
- The user's directory tree can be displayed graphically.
## 💡 About the project
```



## 🛠️ Usage

Please provide the start and end dates in the format "dd/mm/aaaa" when executing your script. For example:

```
python recovery.py --start 01/01/2022 --end 31/12/2022

```
if you do not set any date, it will take certain default values, which by default are 30 days.
