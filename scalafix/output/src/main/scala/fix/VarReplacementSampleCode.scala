package fix

import scala.{Int => BaseContext}
import scala.Int
import scala.Boolean
import scala.util.Try

trait VarReplacementSampleCode {
  def fun1a(implicit context: BaseContext): Unit
  def fun1()(implicit context: BaseContext): Unit
  def fun1(i: Int)(implicit context: BaseContext): Unit
  def fun1b(i: Int)()(implicit context: BaseContext): Unit
  def fun1(implicit c: Int, b: Int, context: BaseContext): Unit
  def fun1c()(implicit c: Int, b: Int, context: BaseContext): Unit

  def fun2(implicit context: BaseContext) = {val b = (); s"s"}
  def fun2b()(implicit context: BaseContext) = {val b = (); s"s"}
  def fun2c()(implicit context: BaseContext): Unit = {()}
  def fun2(i: Int)(implicit context: BaseContext): Unit = {()}
  def fun2b(i: Int)()(implicit context: BaseContext): Unit = {()}
  def fun2(i: Int)(a: Int)(f: Int => Int)(implicit b: Int, context: BaseContext): Unit = {()}
  def fun211(i: Int, j: Int)(a: Int)(f: Int => Int)(implicit bi: Int, context: BaseContext): Unit = {()}
  def fun211(i: Int)(a: Int)(f: Int => Int)(implicit bi: Int, context: BaseContext) = {()}
}