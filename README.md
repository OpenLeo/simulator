# Leo Simulator 2000

Debug tool for AEE2004 can networks

## Warning

This is only a debug and reverse engineering tool, it is **not designed to be used in a real car.
It is also pretty messy, be aware that bugs can, and will probably happens

## What is it

This is a tool made to debug and reverse engineer CAN frames and ECUs. This was built to serve two purposes: sending frames to an existing ECU to check how it reacts to specific data being sent to it, and be used as a bench car simulator for custom ECUs so they can still read "data from a car" (even if the car is actually being emulated)

## How it works

This is a python+kivy app that connect to a socketcan network (hardcoded for now... can0), and load "modules" that are a panel (loaded in a tab) and several CAN handlers. each module is meant to simulate a specific part of the car (for example, the CD part of the radio, or the cluster frames from the BSI)

## Requirements

Python3, kivy and a socketcan network named `can0` (for example, a CANAble interface, or a virtual can interface)
