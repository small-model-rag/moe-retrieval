import {config} from "dotenv"

config()

export function getRequiredEnvVar(varName: string) {
    const value = process.env[varName]
    if (value === undefined) {
        throw new Error(`${varName} env var missing`)
    }
    return value
}

export function getRequiredNumericEnvVar(varName: string) {
    const varValue = getRequiredEnvVar(varName)
    const number = parseInt(varValue)
    if (isNaN(number))
        throw new Error(`Invalid numeric value for env var: ${varName}`)

    return number
}

export function getNumericEnvVarWithDefault(varName: string, defaultValue: number) {
    const varValue = process.env[varName]
    if (varValue === undefined)
        return defaultValue

    let number = parseInt(varValue);

    if (isNaN(number))
        return defaultValue

    return number
}