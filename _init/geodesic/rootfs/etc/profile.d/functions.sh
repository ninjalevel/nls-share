#!/bin/bash

echo "[sourced] etc/profile.d/functions.sh"

function hg() {
    history | grep "$@"
}
