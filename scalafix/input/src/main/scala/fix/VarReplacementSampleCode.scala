/*
rule = AddContextVarV1
*/
package fix

import scala.Int
import scala.Boolean
import scala.{Int => BaseContext}

trait VarReplacementSampleCode {
  private[common] def refreshActions(): Seq[Boolean] = {Seq(false)}

  def fun1a: Unit
  def fun1(): Unit
  def fun1(i: Int): Unit
  def fun1b(i: Int)(): Unit
  def fun1(implicit c: Int, b: Int): Unit
  def fun1c()(implicit c: Int, b: Int): Unit

  def fun2 = {val b = (); s"s"}
  def fun2b() = {val b = (); s"s"}
  def fun2c(): Unit = {()}
  def fun2(i: Int): Unit = {()}
  def fun2b(i: Int)(): Unit = {()}
  def fun2(i: Int)(a: Int)(f: Int => Int)(implicit b: Int): Unit = {()}
  def fun211(i: Int, j: Int)(a: Int)(f: Int => Int)(implicit bi: Int): Unit = {()}
  def fun211(i: Int)(a: Int)(f: Int => Int)(implicit bi: Int) = {()}
}