import chalk from "chalk";

export const logger = {
  info: (msg: string) => console.log(chalk.blue("info"), msg),
  success: (msg: string) => console.log(chalk.green("success"), msg),
  warn: (msg: string) => console.log(chalk.yellow("warn"), msg),
  error: (msg: string) => console.log(chalk.red("error"), msg),

  title: (msg: string) => console.log(chalk.bold.cyan(`\n${msg}\n`)),
  dim: (msg: string) => console.log(chalk.dim(msg)),
};
