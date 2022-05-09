[TOC]

## The rules

Anysocks predefined process rule is a convenient way to proxy some already known programs without adding rules for them manually.

 

## Ⅰ: Dir tree

+ **icons**

  > All the icons that referenced by rules.

+ **rules**

  > All the rule files (`.json`)

+ **scripts**

  > Some utility python scripts
  >
  > + `extract_icon.py` will help you automatically extract and optimize the ICON from EXE and place into the `icons` directory.
  >
  >   > `extract_icon.bat` is a wrapper of this script.
  >
  > + `gen_guid.py` will generate a random GUID for you.
  >
  > + `template.bat` can be used to generate a template config file with GUID filled in place.

  

## Ⅱ: Categories

+ **POPULARS**

  > Popular apps such as `Telegram`, `Chrome`, `Spotify` and so on.

+ **GAMES**

  > Consist of all game associated stuffs
  >
  > + Game platform `Steam`,  `Origin`, etc.
  > + Anti-cheat components `EAC`, `BattleEye`, etc .
  > + Tools like `Discord`, `Xbox app`, etc.

+ **PROGRAMMING**

  > Programming associated apps, like IDE, VCS, Package manager and so on.

+ **PRODUCTIVITY**

  > + DCC tools like `Substance`, `Unreal Engine` , etc
  > + Office tools `Word`, `Excel`
  > + Movie editing tools
  > + And so on

+ **SYSTEM**

  > Windows system installed apps, like `Microsfot Store`, `IE` , etc.

+ **GENERIC**

  > Normal some programs like browsers, downloader, IM, streaming platform, and much more.

+ **OTHERS**

  > All the software which can not fall into the above categories.

 

## Ⅲ: Rule

Literally a rule is a `.json` file, the top level could be either:

+ An array

  > Indicate this file consist of multiple rules.

+ An object

  > Indicate this file contains only single one rule.

Here is a straightforward example to demonstrate what a rule loos like:

```javascript
//
// Array indicate it contains multiple rules.
//
[
  //
  // A single rule object
  //
  {
    //
    // You can use scripts/gen_guid.bat to generate a GUID
    //
    "guid": "{3EF46BB7-52FF-4E86-A303-F4D927E5ED93}",
    //
    // One of [POPULARS, GAMES, PROGRAMMING, SYSTEM, GENERIC, OTHERS]
    //
    "category": "GAMES",
    //
    // Rule's name
    //
    "name": "Steam",
    //
    // Further description of this rule (optional)
    //
    "description": "The steam platform itself, not including games",
    //
    // Reference to the icons/steam.ico file
    //
    "icon": "steam.ico",
    //
    // Multiple file path match expressions.
    //
    "rules": [
      "steam.exe",
      "*\\bin\\cef\\*\\*.exe"
    ],
    //
    // Sometimes a rule may rely on some other independent rules.
    // For example, many network games (PUBG, Call Of Duty) rely on some           
    // sort of anti-cheat programs such as EAC, BatteEye, and so on.
    //
    "dependencies": [
      "{9907e4d7-5ec6-408d-9fc7-adc96f3cd1a2}"
    ]
  },
  //
  // A single rule object
  //
  {
    "guid": "{88247AB3-0D94-48D7-95C1-7162E2C390F6}",
    "category": "GAMES",
    "name": "Steam games",
    "description": "All the steam games",
    "icon": "steam.ico",
    "rules": [
      "*\\steamapps\\common\\*"
    ]
  }
]
```

